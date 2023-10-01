import asyncio
import json
import threading
import time

from fastapi import WebSocket
from our_celery_manager.app.celery import celeryapp

import logging
from celery.app.control import Inspect
from celery.events.receiver import EventReceiver
from celery.events.state import State

logger = logging.getLogger(__name__)


class CeleryClusterInformationObserver:
    def on_event(self, evt, state: State):
        pass

    def on_registered(self, registered):
        pass


class RelayToWebsocket(CeleryClusterInformationObserver):
    """Event observer which relays to a websocket"""

    def __init__(self, ws: WebSocket) -> None:
        super().__init__()
        self._ws = ws

    # TODO: have a best definition of the format to send
    def on_event(self, evt, state):
        content = json.dumps(evt)
        asyncio.run(
            self._ws.send_text(content)
        )  # XXX: on purpose, maybe it should be changed
        return super().on_event(evt, state)

    def on_registered(self, registered):
        content = json.dumps(registered)
        asyncio.run(
            self._ws.send_text(content)
        )  # XXX: on purpose, maybe it should be changed
        return super().on_registered(registered)


class CeleryClusterInformationSubject:
    """A subject emitting celery information such as events and diverse data from inspect API"""

    def __init__(self):
        self._recv: EventReceiver | None
        self._stop_pollinspect = False
        self._observers: list[CeleryClusterInformationObserver] = []
        self._state: State = celeryapp.events.State()
        self._inspect: Inspect = celeryapp.control.inspect()
        self._thread_events = threading.Thread(target=self._capture_events)
        self._thread_pollinspect = threading.Thread(target=self._poll_inspect)
        self._thread_events.start()
        self._thread_pollinspect.start()

    def close(self):
        self._recv.should_stop = True
        self._stop_pollinspect = True
        self._thread_pollinspect.join()
        self._thread_events.join()

    def add_observer(self, obs: CeleryClusterInformationObserver):
        self._observers.append(obs)
        logger.debug(f"Adding an event observer 👁. Got {len(self._observers)} peepers.")

    def remove_observer(self, obs: CeleryClusterInformationObserver):
        self._observers.remove(obs)
        logger.debug(
            f"Removed an event observer 👁. Got {len(self._observers)} peepers."
        )

    def _capture_events(self):
        with celeryapp.connection_for_read() as conn:
            self._recv: EventReceiver = celeryapp.events.Receiver(
                conn, handlers={"*": self._handle_event}
            )
            logger.debug(" 📸 Capturing celery events")
            self._recv.capture(limit=None, timeout=None)
            logger.debug(" 📷 Captured events, bye bye")

    def _handle_event(self, evt):
        self._state.event(evt)
        for peeper in self._observers:
            peeper.on_event(evt, self._state)

    def _poll_inspect(self):
        step = 5
        last = time.monotonic()

        while not self._stop_pollinspect:
            current = time.monotonic()
            elapsed = current - last
            if elapsed < step:
                time.sleep(step - elapsed)
                continue

            logger.debug(" ➿ polling ")
            registered = self._inspect.registered()
            last = time.monotonic()
            for peeper in self._observers:
                peeper.on_registered(registered)

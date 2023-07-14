# Our Celery Manager

Operational tool around the message broker [Celery](https://docs.celeryproject.org/en/stable/index.html).

Specifically, it is a query interface for tasks stored in the [result backend](https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-result-backend-settings).

*This tool is only compatible with a result backend that uses a SQL database.*

## Features

- Web interface to visualize tasks results and states (success, failure, etc.) from the celery result backend
- Button to relaunch a task with same name, arguments. (Better use this feature with idempotent tasks)

## Development Documentation

[DEV_README.md](./DEV_README.md)

## Examples of docker-compose files

See folder [examples](./examples/composes/)

## Screenshot

![Interface](screenshot.png)
# Our Celery Manager

Operational tool around the message broker [Celery](https://docs.celeryproject.org/en/stable/index.html).

Specifically, it is a query interface for tasks stored in the [result backend](https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-result-backend-settings).

*This tool is only compatible with a result backend that uses a SQL database.*

## Features

- Web interface to visualize tasks results and states (success, failure, etc.) from the celery result backend
- Button to relaunch a task with same name, arguments. (Better use this feature with idempotent tasks)
- Additional tasks metadata for monitoring logic - see below for a rationale

### Our celery manager additional task metadata

Currently, the result backend loose some information about task context (e.g [parent id of a task is not stored](https://https://github.com/celery/celery/issues/5824)), or requires specific client code to correctly store/restore context ([example with GroupResult](https://github.com/celery/celery/issues/4516))

Also, we would like to be able to hint the celery manager tool about its behavior directly from the client code.

That's why we chose to setup a convention for storing additional metadata in the result backend. This convention is based on the kwargs of the task. Here are the keys used:

| kwarg                      | Accepted values       | description                                                     |
|----------------------------|-----------------------|-----------------------------------------------------------------|
| `ocm_parent_id`            | UUID of a parent task | Specify the parent id of the task at hand to our-celery-manager |


## Development Documentation

[DEV_README.md](./DEV_README.md)

## Examples of docker-compose files

See folder [examples](./examples/composes/)

## Screenshot

![Interface](screenshot.png)
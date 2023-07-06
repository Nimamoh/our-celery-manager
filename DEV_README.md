# README.md

Consists of two applications:

- [api](./api/): Python backend that serves the APIs
- [front](./front/): Vue frontend

**Currently, the frontend is embedded in the `api` application via the [static](./api/app/static/) folder.**

## Environment Variables

| Name              | Description                                                                                                                           |                                                         |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| APPLICATION_NAME  | Name of the application                                                                                                               | `Our celery manager`                                    |
| BROKER            | Celery broker address                                                                                                                 | `redis://redis:6379/0`                                  |
| BACKEND           | Result backend address                                                                                                                | `db+postgresql://user:password@127.0.0.1:5432/database` |
| ROOT_PATH         | The `path prefix` for a potential proxy, see [FastAPI - behind a proxy](https://https://fastapi.tiangolo.com/advanced/behind-a-proxy/) | `/prefix/`                                              |

## API Application

### Generate `requirements.txt`

```bash
pip install pip-tools
pip-compile --resolver=backtracking requirements.in \
        && pip-compile --resolver=backtracking dev-requirements.in
pip-sync requirements.txt dev-requirements.txt
```

### Generate TypeScript client

Start the API locally and run the following command:

```fish
docker run --rm --network="host" --add-host host.docker.internal:host-gateway -v (pwd)":/local" openapitools/openapi-generator-cli generate \
        -i http://host.docker.internal:8000/openapi.json \
        -g typescript-fetch \
        -p modelPropertyNaming=original \
        -o /local/src/generated/api
```

### Frontend Application

Located in the [front](./front/) folder.

It is a Vue application that uses [https://primevue.org/](https://https://primevue.org/) as a UI framework.

```bash
# Install dependencies
npm ci
```

```bash
# For development
npm run dev
# Pour installer l'application frontend dans les statiques servis par python
npm run build
```

### Setup a simple development environment

Go to the [examples](./examples/composes/) folder and run:

```bash
docker-compose up -d
```

## TODO:

- [x] Improve table
- [x] Append hash to static resources.
- [ ] Order is lost during sorting.
- [x] <strike>Timezone configurable on dates.</strike> Apply correct timezone to date_done.
- [ ] Filter by day or date range.
- [ ] Select and add in bulk.
- [x] Know the maximum number of pages.
- [ ] Task hierarchy
  - [ ] Currently not possible as the parent id is not persisted: issue

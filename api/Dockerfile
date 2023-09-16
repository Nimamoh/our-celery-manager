FROM python:3.11.5-alpine

EXPOSE 80

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 pip install psycopg[c,pool]~=3.1  && \
 apk --purge del .build-deps

WORKDIR /code
COPY . /code

RUN pip install -r requirements.txt 

ARG VERSION=development
RUN echo "$VERSION" > /code/src/our_celery_manager/app/VERSION

RUN pip install .

# EXPOSE
CMD [ "uvicorn", "our_celery_manager.app.main:app", "--host", "0.0.0.0", "--port", "80" ]
FROM python:3.11.3-alpine

EXPOSE 80

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN apk add --no-cache build-base \
  && pip install -r requirements.txt \
  && apk del --no-cache build-base

COPY ./app /code/app

ARG VERSION=development
RUN echo "$VERSION" > /code/app/VERSION

# EXPOSE
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80" ]
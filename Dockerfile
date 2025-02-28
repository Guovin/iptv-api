FROM python:3.13-alpine AS builder

ARG LITE=False

WORKDIR /app

COPY Pipfile* ./

RUN apk update && apk add --no-cache gcc musl-dev python3-dev libffi-dev zlib-dev jpeg-dev \
  && pip install pipenv \
  && PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy \
  && if [ "$LITE" = False ]; then pipenv install selenium; fi

FROM python:3.13-alpine

ARG APP_WORKDIR=/iptv-api
ARG LITE=False

ENV APP_WORKDIR=$APP_WORKDIR
ENV LITE=$LITE
ENV APP_PORT=8000
ENV PATH="/.venv/bin:$PATH"
ENV UPDATE_CRON="0 22,10 * * *"

WORKDIR $APP_WORKDIR

COPY . $APP_WORKDIR

COPY --from=builder /app/.venv /.venv

RUN apk update && apk add --no-cache dcron ffmpeg \
  && if [ "$LITE" = False ]; then apk add --no-cache chromium chromium-chromedriver; fi

EXPOSE $APP_PORT

COPY entrypoint.sh /iptv-api-entrypoint.sh

COPY config /iptv-api-config

RUN chmod +x /iptv-api-entrypoint.sh

ENTRYPOINT /iptv-api-entrypoint.sh
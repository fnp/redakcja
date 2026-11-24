FROM python:3.10-slim-trixie AS base

ARG UID=8200
ARG GID=8200

COPY requirements/requirements.txt requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

RUN addgroup --gid $GID app && \
    adduser --gid $GID --home /app --uid $UID app

USER app

WORKDIR /app/src




FROM base AS dev

USER root
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir coverage
USER app




FROM base AS prod-base

USER root

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir gunicorn

USER app

COPY src /app/src



FROM prod-base AS static-builder

RUN python manage.py collectstatic --noinput


FROM nginx:alpine AS nginx

ARG UID=8200
ARG GID=8200

COPY scripts/nginx.conf /etc/nginx/conf.d/default.conf

RUN addgroup -g $GID app && addgroup nginx app
COPY --from=static-builder /app/src/static /app/var/static




FROM prod-base AS prod

COPY --from=static-builder /app/src/static/staticfiles.json /app/src/static/staticfiles.json

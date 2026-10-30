FROM python:3.10-trixie AS base

ARG UID=8200
ARG GID=8200

RUN     apt-get update && apt-get install -y \
        # for epubcheck
        default-jre \
	git \
	calibre \
	texlive-xetex texlive-lang-polish \
	texlive-extra-utils \
	texlive-lang-greek \
	texlive-lang-other \
	texlive-luatex \
	texlive-fonts-extra \
	texlive-fonts-extra-links \
	fonts-noto-core fonts-noto-extra


COPY requirements/requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN wget https://github.com/w3c/epubcheck/releases/download/v5.3.0/epubcheck-5.3.0.zip && \
    unzip epubcheck-5.3.0.zip && \
    rm epubcheck-5.3.0.zip && \
    mv epubcheck-5.3.0 /opt/epubcheck


RUN addgroup --gid $GID app && \
    adduser --gid $GID --home /app --uid $UID app


# fonts
RUN cp -a /usr/local/lib/python*/site-packages/librarian/fonts /usr/share/fonts
RUN fc-cache

USER app

WORKDIR /app/src


FROM base AS dev

USER root
RUN pip install --no-cache-dir coverage
USER app




FROM base AS prod-base

USER root

RUN pip install --no-cache-dir gunicorn

USER app

COPY src /app/src





FROM prod-base AS static-builder

RUN python manage.py collectstatic --noinput




FROM nginx:alpine AS nginx

ARG UID=8200
ARG GID=8200

# COPY nginx.conf conf.d/...

RUN addgroup -g $GID app && addgroup nginx app
COPY --from=static-builder /app/var/static /app/var/static




FROM base AS prod

COPY --from=static-builder /app/var/static/staticfiles.json /app/var/static/staticfiles.json

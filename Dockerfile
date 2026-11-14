FROM python:3.12-slim AS base
LABEL maintainer="Akash Talole <taloleakash@gmail.com>"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

##
## Builder: installs the Python dependencies into /install
##
FROM base AS builder

WORKDIR /install

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev libffi-dev libjpeg-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
COPY requirements /requirements/

RUN pip install --prefix=/install -r /requirements.txt

##
## Final image
##
FROM base

# libmagic is needed by python-magic, libpq by psycopg2, the rest by Pillow / xhtml2pdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends libmagic1 libpq5 libjpeg62-turbo zlib1g ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --uid 10001 appuser

COPY --from=builder /install /usr/local

WORKDIR /data/app
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8080
CMD ["sh", "scripts/container_start.sh"]

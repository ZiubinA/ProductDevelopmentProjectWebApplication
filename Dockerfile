FROM python:3.12-alpine3.20

RUN apk add --no-cache \
    build-base \
    libpq-dev \
    musl-dev \
    libxml2-dev \
    libxslt-dev

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings

EXPOSE 8080

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8080"]
# Stage 1: build wheels with build dependencies
# FROM python:3.12-slim AS builder
# ENV DEBIAN_FRONTEND=noninteractive

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     libpq-dev \
#     libxml2-dev \
#     libxslt1-dev \
#     && rm -rf /var/lib/apt/lists/*

# WORKDIR /wheels
# COPY requirements.txt .

# # Build wheels for all requirements into /wheels
# RUN python -m pip install --upgrade pip setuptools wheel \
#     && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# # Stage 2: final runtime image (no build deps)
# FROM python:3.12-slim
# ENV DEBIAN_FRONTEND=noninteractive \
#     PYTHONUNBUFFERED=1 \
#     DJANGO_SETTINGS_MODULE=core.settings

# # Install only runtime system libs (not -dev)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libpq5 \
#     libxml2 \
#     libxslt1.1 \
#     && rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# # Copy prebuilt wheels and install them (no compilation in final image)
# COPY --from=builder /wheels /wheels
# COPY requirements.txt .

# RUN python -m pip install --upgrade pip \
#     && pip install --no-cache-dir --no-index --find-links /wheels -r requirements.txt \
#     && rm -rf /wheels

# # Copy app code
# COPY . .

# EXPOSE 8080
# CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8080"]
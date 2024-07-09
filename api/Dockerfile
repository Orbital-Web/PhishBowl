# Stage 1: Build environment
FROM python:3.11-slim AS builder

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Stage 2: Production Environment
FROM python:3.11-slim

COPY --from=builder /usr/local /usr/local

RUN apt-get update \
    && apt-get -y --no-install-recommends install tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "main.py", "run"]
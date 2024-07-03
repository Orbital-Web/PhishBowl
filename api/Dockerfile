FROM python:3.11-slim

RUN apt-get update \
    && apt-get -y install tesseract-ocr

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt

WORKDIR /app
COPY . .

ENV PYTHONPATH=/app

CMD ["python", "main.py", "run"]
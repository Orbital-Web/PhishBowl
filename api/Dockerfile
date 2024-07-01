FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get -y install tesseract-ocr

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["python", "main.py", "run"]
FROM python:3.11-slim

WORKDIR /chroma

RUN pip install --no-cache-dir --upgrade chromadb

COPY . .

EXPOSE 5000

CMD ["chroma", "run", "--host", "0.0.0.0", "--port", "5000"]
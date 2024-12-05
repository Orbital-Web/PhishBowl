FROM python:3.11-slim

WORKDIR /chroma

RUN pip install --no-cache-dir chromadb==0.5.3

COPY . .

EXPOSE 5000

CMD ["chroma", "run", "--host", "0.0.0.0", "--port", "5000"]
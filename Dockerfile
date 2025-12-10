FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Instalar postgresql-client para backups
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app

# Create storage directory
RUN mkdir -p /code/storage

EXPOSE 6076

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "6076", "--reload"]


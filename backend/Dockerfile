FROM python:3.12.9-slim

WORKDIR /app

COPY . .

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-mysql-client \
    && pip install --default-timeout=100 --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
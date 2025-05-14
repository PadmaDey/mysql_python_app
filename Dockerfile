FROM python:3.12.9-slim

WORKDIR /app

COPY . .

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends default-mysql-client \
#     && pip install --no-cache-dir -r requirements.txt \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-mysql-client \
    && pip install --default-timeout=100 --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

CMD ["python", "app.py"]

# docker build -t mysql_conn .
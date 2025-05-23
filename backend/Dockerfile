# FROM python:3.12

# WORKDIR /app

# RUN apt-get update && \
#     apt-get install -y --no-install-recommends gcc python3-dev default-mysql-client

# COPY requirements.txt .

# RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt && \
#     pip install --upgrade pip

# COPY ./app ./app

# RUN apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM python:3.12

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev default-mysql-client curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt && \
    pip install --upgrade pip

# Download wait-for-it.sh to wait for MySQL
RUN curl -o /wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /wait-for-it.sh

COPY ./app ./app

CMD ["/wait-for-it.sh", "mysql:3306", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

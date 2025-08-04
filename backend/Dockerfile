# ===== Stage 1: Build =====
FROM python:3.12-slim AS builder

WORKDIR /app

# Suppress debconf warnings and install build dependencies
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies with root-user-action suppressed
COPY requirements.txt .
RUN pip install --upgrade pip --root-user-action=ignore && \
    pip install --root-user-action=ignore --prefix=/install --no-cache-dir -r requirements.txt

# Download wait-for-it.sh
RUN curl -o /wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /wait-for-it.sh

# ===== Stage 2: Runtime =====
FROM python:3.12-slim

WORKDIR /app

# Suppress debconf warnings and install runtime dependencies
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        default-mysql-client \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local
ENV PATH=/usr/local/bin:$PATH

# Copy application code and wait-for-it.sh
COPY --from=builder /wait-for-it.sh /wait-for-it.sh
COPY ./app ./app

# Expose the application port
EXPOSE 8080

# Run FastAPI app using uvicorn after MySQL is ready
CMD ["/wait-for-it.sh", "mysql:3306", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]


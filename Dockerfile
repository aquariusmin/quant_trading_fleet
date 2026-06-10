# --- Stage 1: Build React Frontend ---
FROM node:18-slim AS build-frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# --- Stage 2: Final Image with FastAPI ---
FROM python:3.11-slim

# Set timezone to KST
ENV TZ=Asia/Seoul
RUN apt-get update && apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Add FastAPI specific dependencies
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy pydantic-settings

# Copy backend code
COPY . .

# Copy built frontend assets from Stage 1
# We will serve these via FastAPI's StaticFiles
COPY --from=build-frontend /frontend/dist /app/frontend/dist

# Ensure database and logs directories exist
RUN mkdir -p /app/backend/database /app/logs

# Run as non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Start FastAPI server
CMD ["python", "backend/main.py"]

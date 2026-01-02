FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Copy server code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8300

# Run server
CMD ["python", "server.py"]

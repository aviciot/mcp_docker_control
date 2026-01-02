FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8300

# Run server
CMD ["python", "server.py"]

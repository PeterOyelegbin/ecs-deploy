FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential netcat-openbsd libssl-dev \
    python3-dev default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create non-root user (ECS best practice)
RUN useradd -m django && chown -R django:django /app
USER django

# Expose port for the server
EXPOSE 8000

# Set entry point
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Run the application with Gunicorn
CMD ["gunicorn", "todo.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2"]

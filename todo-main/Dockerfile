FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential netcat-openbsd libssl-dev python3-dev \
    default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./todo-main/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install cryptography

# Copy project files
COPY ./todo-main/ .

# Expose port for the server
EXPOSE 8000

# Optional: Collect static files
RUN python manage.py collectstatic --noinput || true

# Setup entrypoint
COPY ./todo-main/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# # Run the application with Gunicorn
# CMD ["gunicorn", "todo.wsgi:application", "--bind", "0.0.0.0:8000"]

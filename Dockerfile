# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies required for mysqlclient
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    default-libmysqlclient-dev \
    python3-dev \
    pkg-config \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Expose port
EXPOSE 8000

# Start the Django server
CMD ["python", "news_project/manage.py", "runserver", "0.0.0.0:8000"]

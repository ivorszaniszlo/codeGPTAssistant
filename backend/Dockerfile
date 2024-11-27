# Use a lightweight official Python image as base
FROM python:3.13-slim

# Set environment variables to reduce Python output noise
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy only the requirements file to leverage Docker caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir elasticsearch redis

# Copy the rest of the application code
COPY . .

# Expose the application port
EXPOSE 8000

# Command to run the application in development mode
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


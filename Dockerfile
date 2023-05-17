# Use the official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY app ./app

# Install Gunicorn
RUN pip install gunicorn

# Set the entrypoint command to run the Flask app using Gunicorn
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]

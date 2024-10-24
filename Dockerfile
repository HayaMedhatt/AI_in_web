# Use a base image with Python
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the environment variables (if any)
ENV FLASK_ENV=production

# Expose the port the app runs on
EXPOSE 5000

# Command to run the app
CMD ["python", "app/main.py"]
# Use the official Python base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY app.py .
COPY data /app/data

# Expose the port for the Flask application
EXPOSE 5000

# Set the entrypoint command to run the Flask application
CMD ["python", "app.py"] 
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the Flask app will run on
EXPOSE 5000

# Set the environment variable to tell Flask to run in production mode
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the app when the container starts
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

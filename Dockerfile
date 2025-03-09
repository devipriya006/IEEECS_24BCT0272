# Use an official lightweight Python image as a base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements file first (for better caching)
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the port that Flask runs on
EXPOSE 5000

# Set environment variables (important for production)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV MONGO_URI="mongodb://mongo:27017/cinepass_db"

# Start the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

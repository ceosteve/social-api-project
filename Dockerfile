
# Use Python slim base image
FROM python:3.13-slim

# Set working directory inside container
WORKDIR /app

# Copy only requirements first (to leverage caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Command to run FastAPI using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]



# Use the latest stable Python base image
FROM python:3.12-slim

# Set environment variables
ENV PROJECT_ID=kredoh
ENV SECRET_ID=kredoh-paybill
ENV SECRET_VERSION=13
ENV PORT=7070

# Set working directory
WORKDIR /opt/kredoh-paybill

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Use a non-root user for security
RUN useradd --create-home appuser
USER appuser

# Expose the application port
EXPOSE 7070

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7070"]
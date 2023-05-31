# Use the official Python base image
FROM python:3.8-slim-buster

#project id
ENV PROJECT_ID kredoh

#Secret manage for odoo-erp detais
ENV SECRET_ID kredoh-api
ENV SECRET_VERSION 15

# Set the working directory in the container
RUN mkdir /opt/kredoh-paybill
#RUN mkdir /var/log

WORKDIR /opt/kredoh-paybill

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Set the port number that the container should listen on
ENV PORT=8080

# Command to run the application
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
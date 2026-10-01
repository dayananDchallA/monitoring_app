# Use the official Python base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app files to the container
COPY . .

#Set the entrypoint command to run the app
CMD [ "streamlit","run","main.py" ]
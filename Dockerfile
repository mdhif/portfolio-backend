# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install pipenv
RUN pip install pipenv

# Copy the Pipfile and Pipfile.lock into the container at /app
COPY Pipfile Pipfile.lock /app/

# Install dependencies using pipenv
RUN pipenv install --deploy --ignore-pipfile

# Copy the rest of your application code into the container
COPY . /app/

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define the command to run your FastAPI application
CMD ["pipenv", "run","python", "serve.py"]

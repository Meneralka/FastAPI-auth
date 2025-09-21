# Use a slim Python 3.12 base image for a smaller footprint
FROM python:3.12-slim

# Set the working directory inside the container to /app
WORKDIR /app/auth

# Install Poetry as the dependency manager
RUN pip install --no-cache-dir poetry

# Copy the Poetry configuration files to install dependencies
COPY pyproject.toml poetry.lock /app/

# Configure Poetry to install packages directly into the system environment (no virtualenv)
RUN poetry config virtualenvs.create false

# Install project dependencies without development ones for production
RUN poetry install --no-root --without dev --no-interaction --no-ansi

# Copy the source code directory into the container
COPY auth /app/auth

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Set the command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "main:main_app", "--host", "0.0.0.0", "--port", "8000"]
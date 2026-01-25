# Multi-stage build for the Python backend application
# Stage 1: Build dependencies
FROM python:3.11-alpine AS deps

# Install build tools needed for some Python packages
RUN apk add --no-cache gcc musl-dev libffi-dev

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Create the production image
FROM python:3.11-alpine

# Install runtime dependencies
RUN apk add --no-cache bash curl dumb-init

WORKDIR /app

# Copy installed dependencies from the deps stage
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy only necessary application files
COPY .env.example ./
COPY main.py ./
COPY alembic.ini ./
COPY requirements.txt ./
COPY api/ ./api/
COPY database/ ./database/
COPY models/ ./models/
COPY services/ ./services/
COPY src/ ./src/
COPY pyproject.toml ./
COPY analytics.py ./
COPY test_chat_endpoint.py ./
COPY test_gemini_chatbot.py ./
COPY test_integration.py ./
COPY e2e_test.py ./
COPY install_requirements.sh ./
COPY install_requirements.bat ./
COPY mcp/ ./mcp/

# Create a non-root user for security
RUN addgroup -g 1001 -S python &&\
    adduser -S python -u 1001

# Change ownership of the app directory to the non-root user
RUN chown -R python:python /app
USER python

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application with uvicorn
ENTRYPOINT ["dumb-init", "--"]
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
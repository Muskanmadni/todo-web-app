#!/bin/bash

# Test script to verify frontend and backend containers locally
set -e

echo "Starting local container tests..."

# Test frontend container
echo "Building frontend container..."
cd ../todo-frontend
docker build -t todo-frontend:test .

echo "Running frontend container..."
FRONTEND_CONTAINER_ID=$(docker run -d -p 3000:3000 --name test-frontend todo-frontend:test)

# Wait for the container to start
sleep 10

# Test if frontend is accessible
if curl -f -s "http://localhost:3000" > /dev/null; then
    echo "✓ Frontend container is running and accessible"
else
    echo "✗ Frontend container is not accessible"
    docker logs test-frontend
    docker stop test-frontend
    docker rm test-frontend
    exit 1
fi

# Stop and remove frontend container
docker stop test-frontend
docker rm test-frontend

# Test backend container
echo "Building backend container..."
cd ../todo-backend
docker build -t todo-backend:test .

echo "Running backend container..."
BACKEND_CONTAINER_ID=$(docker run -d -p 8000:8000 --name test-backend todo-backend:test)

# Wait for the container to start
sleep 10

# Test if backend is accessible
if curl -f -s "http://localhost:8000/health" > /dev/null; then
    echo "✓ Backend container is running and accessible"
else
    echo "✗ Backend container is not accessible"
    docker logs test-backend
    docker stop test-backend
    docker rm test-backend
    exit 1
fi

# Stop and remove backend container
docker stop test-backend
docker rm test-backend

echo "Testing inter-container communication..."
# For this test, we'll simulate communication by running both containers in a shared network
docker network create test-network || true

# Run backend first
docker run -d --network test-network --name test-backend-communication -e DATABASE_URL="sqlite:///test.db" todo-backend:test

# Wait for backend to be ready
sleep 15

# Run frontend and link to backend
docker run -d --network test-network --name test-frontend-communication -e REACT_APP_API_URL="http://test-backend-communication:8000" todo-frontend:test

# Wait for both to be ready
sleep 10

# Test communication
if docker exec test-frontend-communication curl -f -s "http://test-backend-communication:8000/health" > /dev/null; then
    echo "✓ Inter-container communication works"
else
    echo "✗ Inter-container communication failed"
    docker logs test-backend-communication
    docker logs test-frontend-communication
    docker stop test-frontend-communication
    docker stop test-backend-communication
    docker rm test-frontend-communication
    docker rm test-backend-communication
    docker network rm test-network
    exit 1
fi

# Clean up
docker stop test-frontend-communication
docker stop test-backend-communication
docker rm test-frontend-communication
docker rm test-backend-communication
docker network rm test-network

echo "All container tests completed successfully!"
#!/bin/bash

# Deployment script using Helm
set -e

echo "Starting deployment of Todo application..."

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo "Starting Minikube..."
    minikube start
fi

# Enable ingress addon
minikube addons enable ingress

echo "Building Docker images..."

# Build frontend image
echo "Building frontend image..."
cd ../todo-frontend
if command -v gordon &> /dev/null; then
    echo "Using Docker AI Agent (Gordon) to build frontend image..."
    gordon build-image -t todo-frontend:latest .
else
    echo "Gordon not available, falling back to standard Docker CLI..."
    docker build -t todo-frontend:latest .
fi

# Build backend image
echo "Building backend image..."
cd ../todo-backend
if command -v gordon &> /dev/null; then
    echo "Using Docker AI Agent (Gordon) to build backend image..."
    gordon build-image -t todo-backend:latest .
else
    echo "Gordon not available, falling back to standard Docker CLI..."
    docker build -t todo-backend:latest .
fi

# Load images into Minikube
echo "Loading images into Minikube..."
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# Go back to the root directory
cd ..

# Install backend chart first
echo "Installing backend Helm chart..."
helm upgrade --install todo-backend ./todo-backend/helm-chart \
  --set image.repository=todo-backend \
  --set image.tag=latest

# Install frontend chart
echo "Installing frontend Helm chart..."
helm upgrade --install todo-frontend ./todo-frontend/helm-chart \
  --set image.repository=todo-frontend \
  --set image.tag=latest \
  --set backendServiceUrl=http://todo-backend-svc

echo "Deployment completed successfully!"
echo "Access the application at: $(minikube ip)"
#!/bin/bash

# Scaling script using kubectl-ai
set -e

SERVICE_NAME=$1
REPLICAS=$2

if [ -z "$SERVICE_NAME" ] || [ -z "$REPLICAS" ]; then
    echo "Usage: $0 <service-name> <replicas>"
    echo "Example: $0 frontend 3"
    exit 1
fi

echo "Scaling $SERVICE_NAME service to $REPLICAS replicas..."

# Determine the deployment name based on service
if [ "$SERVICE_NAME" = "frontend" ]; then
    DEPLOYMENT_NAME="todo-frontend"
elif [ "$SERVICE_NAME" = "backend" ]; then
    DEPLOYMENT_NAME="todo-backend"
else
    echo "Unknown service name: $SERVICE_NAME"
    exit 1
fi

# Try to use kubectl-ai first
if command -v kubectl-ai &> /dev/null; then
    echo "Using kubectl-ai for scaling..."
    kubectl ai scale deployment $DEPLOYMENT_NAME --replicas=$REPLICAS
else
    echo "kubectl-ai not available, falling back to standard kubectl..."
    kubectl scale deployment $DEPLOYMENT_NAME --replicas=$REPLICAS
fi

echo "Scaling completed!"
echo "Current status:"
kubectl get deployments $DEPLOYMENT_NAME
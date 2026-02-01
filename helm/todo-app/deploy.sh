#!/bin/bash

# Deployment script for Todo App with AI-powered chatbot
# This script sets up the complete infrastructure for the application

set -e  # Exit on any error

echo "🚀 Starting deployment of Todo App with AI-powered chatbot..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl and try again."
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "❌ helm is not installed. Please install helm and try again."
    exit 1
fi

# Check if dapr is available
if ! command -v dapr &> /dev/null; then
    echo "❌ dapr is not installed. Please install dapr and try again."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install Dapr to the cluster if not already installed
echo "🔍 Checking Dapr installation..."
if ! kubectl get ns dapr-system &> /dev/null; then
    echo "📦 Installing Dapr to Kubernetes cluster..."
    dapr init -k
    echo "✅ Dapr installed successfully"
else
    echo "✅ Dapr is already installed"
fi

# Wait for Dapr to be ready
echo "⏳ Waiting for Dapr to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/part-of=dapr -n dapr-system --timeout=300s

# Add the Kafka repository
echo "📦 Adding Kafka repository..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Kafka/Redpanda for event streaming
echo "📦 Installing Kafka for event streaming..."
if ! helm status kafka &> /dev/null; then
    helm install kafka bitnami/kafka --set replicaCount=1 --set auth.enabled=false --set persistence.enabled=false
else
    echo "⚠️ Kafka is already installed"
fi

# Wait for Kafka to be ready
echo "⏳ Waiting for Kafka to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka --timeout=300s

# Install the application
echo "📦 Installing Todo App..."
if helm status todo-app &> /dev/null; then
    echo "🔄 Upgrading existing Todo App installation..."
    helm upgrade todo-app . --values values.yaml
else
    echo "🏗️ Installing new Todo App..."
    helm install todo-app . --values values.yaml
fi

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=ready pod -l app=todo-backend --timeout=300s || true
kubectl wait --for=condition=ready pod -l app=todo-frontend --timeout=300s || true

# Get the service information
echo "🔍 Getting service information..."
kubectl get svc

# Instructions for accessing the application
echo "🎉 Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Get the external IP for the frontend service:"
echo "   kubectl get svc todo-frontend"
echo ""
echo "2. Access the application at http://<EXTERNAL-IP>:3000"
echo ""
echo "3. To view application logs:"
echo "   kubectl logs -l app=todo-backend"
echo "   kubectl logs -l app=todo-frontend"
echo ""
echo "4. To check Dapr sidecars:"
echo "   kubectl get pods -l app=todo-backend -o yaml | grep dapr.io/app-id"
echo "   kubectl get pods -l app=todo-frontend -o yaml | grep dapr.io/app-id"
echo ""
echo "5. To uninstall:"
echo "   helm uninstall todo-app"
echo "   helm uninstall kafka"
echo "   dapr uninstall -k"
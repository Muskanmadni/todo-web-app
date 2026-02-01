# PowerShell deployment script for Todo App with AI-powered chatbot
# This script sets up the complete infrastructure for the application

Write-Host "🚀 Starting deployment of Todo App with AI-powered chatbot..." -ForegroundColor Green

# Check if kubectl is available
if (!(Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Host "❌ kubectl is not installed. Please install kubectl and try again." -ForegroundColor Red
    exit 1
}

# Check if helm is available
if (!(Get-Command helm -ErrorAction SilentlyContinue)) {
    Write-Host "❌ helm is not installed. Please install helm and try again." -ForegroundColor Red
    exit 1
}

# Check if dapr is available
if (!(Get-Command dapr -ErrorAction SilentlyContinue)) {
    Write-Host "❌ dapr is not installed. Please install dapr and try again." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green

# Install Dapr to the cluster if not already installed
Write-Host "🔍 Checking Dapr installation..." -ForegroundColor Yellow
$daprNsExists = kubectl get ns dapr-system 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "📦 Installing Dapr to Kubernetes cluster..." -ForegroundColor Yellow
    dapr init -k
    Write-Host "✅ Dapr installed successfully" -ForegroundColor Green
} else {
    Write-Host "✅ Dapr is already installed" -ForegroundColor Green
}

# Wait for Dapr to be ready
Write-Host "⏳ Waiting for Dapr to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app.kubernetes.io/part-of=dapr -n dapr-system --timeout=300s

# Add the Kafka repository
Write-Host "📦 Adding Kafka repository..." -ForegroundColor Yellow
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Kafka/Redpanda for event streaming
Write-Host "📦 Installing Kafka for event streaming..." -ForegroundColor Yellow
$kafkaStatus = helm status kafka 2>$null
if ($LASTEXITCODE -ne 0) {
    helm install kafka bitnami/kafka --set replicaCount=1 --set auth.enabled=$false --set persistence.enabled=$false
} else {
    Write-Host "⚠️ Kafka is already installed" -ForegroundColor Yellow
}

# Wait for Kafka to be ready
Write-Host "⏳ Waiting for Kafka to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka --timeout=300s

# Install the application
Write-Host "📦 Installing Todo App..." -ForegroundColor Yellow
$todoAppStatus = helm status todo-app 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "🔄 Upgrading existing Todo App installation..." -ForegroundColor Yellow
    helm upgrade todo-app . --values values.yaml
} else {
    Write-Host "🏗️ Installing new Todo App..." -ForegroundColor Yellow
    helm install todo-app . --values values.yaml
}

# Wait for deployments to be ready
Write-Host "⏳ Waiting for deployments to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=todo-backend --timeout=300s -ErrorAction SilentlyContinue
kubectl wait --for=condition=ready pod -l app=todo-frontend --timeout=300s -ErrorAction SilentlyContinue

# Get the service information
Write-Host "🔍 Getting service information..." -ForegroundColor Yellow
kubectl get svc

# Instructions for accessing the application
Write-Host "🎉 Deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Get the external IP for the frontend service:"
Write-Host "   kubectl get svc todo-frontend"
Write-Host ""
Write-Host "2. Access the application at http://<EXTERNAL-IP>:3000"
Write-Host ""
Write-Host "3. To view application logs:"
Write-Host "   kubectl logs -l app=todo-backend"
Write-Host "   kubectl logs -l app=todo-frontend"
Write-Host ""
Write-Host "4. To check Dapr sidecars:"
Write-Host "   kubectl get pods -l app=todo-backend -o yaml | Select-String 'dapr.io/app-id'"
Write-Host "   kubectl get pods -l app=todo-frontend -o yaml | Select-String 'dapr.io/app-id'"
Write-Host ""
Write-Host "5. To uninstall:"
Write-Host "   helm uninstall todo-app"
Write-Host "   helm uninstall kafka"
Write-Host "   dapr uninstall -k"
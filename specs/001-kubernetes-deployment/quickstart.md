# Quickstart Guide: Kubernetes Deployment

## Prerequisites

Before deploying the Todo application to Kubernetes, ensure you have the following tools installed:

- Docker Desktop (with Kubernetes enabled) or Minikube
- Helm 3.x
- kubectl
- kubectl-ai (optional, for AI-assisted operations)
- kagent (optional, for advanced AIOps tasks)

## Setup Instructions

### 1. Start Minikube

```bash
minikube start
```

### 2. Enable required Minikube addons (optional but recommended)

```bash
minikube addons enable ingress
minikube addons enable metrics-server
```

### 3. Clone or navigate to the project directory

```bash
cd path/to/todo-application
```

## Building Docker Images

### Using Docker AI Agent (Gordon) - Preferred Method

```bash
# Navigate to frontend directory
cd todo-frontend

# Use Gordon to create Dockerfile (if not already present)
gordon create-dockerfile .

# Build the image
gordon build-image -t todo-frontend:latest .

# Navigate to backend directory
cd ../todo-backend

# Use Gordon to create Dockerfile (if not already present)
gordon create-dockerfile .

# Build the image
gordon build-image -t todo-backend:latest .
```

### Using Standard Docker CLI - Fallback Method

```bash
# Navigate to frontend directory
cd todo-frontend

# Build the frontend image
docker build -t todo-frontend:latest .

# Navigate to backend directory
cd ../todo-backend

# Build the backend image
docker build -t todo-backend:latest .
```

## Deploying to Kubernetes

### 1. Install Helm charts

```bash
# Navigate to the project root
cd ..

# Install backend chart first (to ensure service is available)
helm install todo-backend ./todo-backend/helm-chart \
  --set image.repository=todo-backend \
  --set image.tag=latest

# Install frontend chart
helm install todo-frontend ./todo-frontend/helm-chart \
  --set image.repository=todo-frontend \
  --set image.tag=latest \
  --set backendServiceUrl=http://todo-backend-svc
```

### 2. Verify deployment

```bash
# Check if pods are running
kubectl get pods

# Check services
kubectl get services

# Check deployments
kubectl get deployments
```

## Accessing the Application

### If using Minikube with ingress

```bash
# Get the Minikube IP
minikube ip

# Access the application at http://<MINIKUBE_IP>
```

### If using LoadBalancer services

```bash
# Get the external IP/Port
kubectl get services

# Access the frontend service using its external IP/Port
```

## Scaling the Application

### Using kubectl-ai (AI-assisted operations)

```bash
# Scale frontend to 3 replicas
kubectl ai scale deployment todo-frontend --replicas=3

# Scale backend to 2 replicas
kubectl ai scale deployment todo-backend --replicas=2
```

### Using standard kubectl

```bash
# Scale frontend to 3 replicas
kubectl scale deployment todo-frontend --replicas=3

# Scale backend to 2 replicas
kubectl scale deployment todo-backend --replicas=2
```

## Monitoring and Health Checks

### Using kagent (Advanced AIOps)

```bash
# Run cluster health analysis
kagent analyze cluster

# Get resource optimization recommendations
kagent optimize resources
```

### Using standard kubectl

```bash
# Check cluster status
kubectl cluster-info

# Get resource usage
kubectl top nodes
kubectl top pods

# Check logs
kubectl logs deployment/todo-frontend
kubectl logs deployment/todo-backend
```

## Troubleshooting

### Common Issues

1. **Images not found**: Ensure Docker images are built and tagged correctly
2. **Service unavailable**: Check if deployments are running and services are properly configured
3. **Ingress not working**: Verify ingress controller is running and rules are correct

### Debugging Commands

```bash
# Describe a pod for detailed information
kubectl describe pod <pod-name>

# Check deployment status
kubectl rollout status deployment/todo-frontend
kubectl rollout status deployment/todo-backend

# View logs for troubleshooting
kubectl logs deployment/todo-frontend
kubectl logs deployment/todo-backend
```

## Cleanup

To remove the deployed application:

```bash
# Uninstall Helm releases
helm uninstall todo-frontend
helm uninstall todo-backend

# Optionally, stop Minikube
minikube stop
```

## Lessons Learned & Best Practices

### Multi-stage Builds
- Use multi-stage builds to optimize Docker images
- Separate build dependencies from runtime dependencies
- Reduce attack surface by using non-root users in production containers

### Security
- Store sensitive data in Kubernetes Secrets, not ConfigMaps
- Run containers as non-root users where possible
- Use minimal base images (e.g., Alpine Linux)

### Configuration Management
- Use Helm for managing Kubernetes manifests
- Parameterize configurations via values.yaml
- Separate environment-specific configurations

### Deployment Strategies
- Deploy backend services first to ensure API availability
- Use health checks (liveness and readiness probes)
- Implement proper resource requests and limits

### Monitoring & Observability
- Implement proper logging in applications
- Use Kubernetes-native monitoring tools
- Set up alerts for critical metrics

## Next Steps

- Configure persistent storage if your application requires it
- Set up monitoring and alerting
- Implement CI/CD pipeline for automated deployments
- Configure TLS/SSL for secure connections
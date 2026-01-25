# Kubernetes Deployment Documentation

## Overview
This document provides comprehensive information about deploying the Todo application on a local Kubernetes cluster using Minikube, Docker, and Helm.

## Prerequisites
- Docker Desktop (with Kubernetes enabled) or Minikube
- Helm 3.x
- kubectl
- kubectl-ai (optional, for AI-assisted operations)
- kagent (optional, for advanced AIOps tasks)

## Deployment Process

### 1. Starting the Local Kubernetes Cluster
```bash
minikube start
minikube addons enable ingress
```

### 2. Building Docker Images
The application uses multi-stage Docker builds for optimization:
- Frontend: Uses a builder stage to build the React app, then serves it with `serve`
- Backend: Uses a builder stage to install dependencies, then runs with a non-root user

To build images manually:
```bash
# Frontend
cd todo-frontend
docker build -t todo-frontend:latest .

# Backend
cd todo-backend
docker build -t todo-backend:latest .
```

### 3. Deploying with Helm
The application consists of two Helm charts:
- `todo-frontend/helm-chart`: Deploys the frontend React application
- `todo-backend/helm-chart`: Deploys the backend API service

To deploy:
```bash
# Install backend first
helm install todo-backend ./todo-backend/helm-chart

# Install frontend
helm install todo-frontend ./todo-frontend/helm-chart
```

### 4. Accessing the Application
Once deployed, access the application using:
```bash
minikube service todo-frontend-svc --url
```

## Scaling the Application

Use the provided scaling script to adjust the number of replicas:
```bash
# Scale frontend to 3 replicas
./scripts/scale-services.sh frontend 3

# Scale backend to 2 replicas
./scripts/scale-services.sh backend 2
```

The script will attempt to use `kubectl-ai` if available, falling back to standard `kubectl` commands.

### Scaling Procedures and Best Practices

1. **Monitor Resource Usage Before Scaling**:
   - Check current resource utilization with `kubectl top nodes` and `kubectl top pods`
   - Understand baseline resource consumption before making scaling decisions

2. **Gradual Scaling**:
   - Scale gradually (e.g., from 1 to 2, then 2 to 3 replicas) rather than jumping directly to a high number
   - Monitor application performance after each scaling operation

3. **Consider Resource Limits**:
   - Ensure your cluster has sufficient resources before scaling up
   - Account for memory and CPU requirements of additional replicas

4. **Verify Application Stability**:
   - After scaling, verify that all replicas are running and healthy
   - Check application logs for any errors related to increased load

5. **Scale Down During Low Traffic**:
   - Scale down during off-peak hours to conserve resources
   - Monitor application performance after scaling down to ensure it can handle the load

6. **Horizontal Pod Autoscaler (HPA)**:
   - For production environments, consider implementing HPA for automatic scaling based on metrics
   - Configure appropriate CPU and memory thresholds for autoscaling

7. **Database Connection Management**:
   - When scaling the backend, ensure your database can handle the increased number of connections
   - Adjust connection pooling settings as needed

## Monitoring and Health Checks

Run health checks using:
```bash
./scripts/health-check.sh
```

The script will attempt to use `kagent` if available, falling back to standard `kubectl` commands.

### Monitoring Procedures and Interpretation of Results

#### Regular Health Checks
1. **Schedule periodic health checks** to monitor cluster status
2. **Set up alerts** for critical issues detected during health checks
3. **Document baseline metrics** to identify anomalies

#### Key Metrics to Monitor
1. **Node Status**:
   - Check that all nodes are in `Ready` state
   - Monitor node resource utilization (CPU, memory, disk)
   - Look for nodes with `DiskPressure`, `MemoryPressure`, or `PIDPressure`

2. **Pod Status**:
   - Verify all pods are in `Running` state
   - Check for pods in `CrashLoopBackOff`, `ImagePullBackOff`, or `Error` states
   - Monitor restart counts for unusual activity

3. **Resource Utilization**:
   - Monitor CPU and memory usage across nodes and pods
   - Identify resource bottlenecks or inefficient resource allocation
   - Track trends in resource consumption over time

4. **Application Health**:
   - Verify that liveness and readiness probes are succeeding
   - Check application logs for errors or warnings
   - Monitor application-specific metrics if available

#### Interpreting Health Check Results
1. **Cluster Information**:
   - Verify cluster endpoints are accessible
   - Check that API server is responding within acceptable timeframes

2. **Node Health**:
   - Investigate nodes with high resource utilization
   - Check for nodes that are not responding to health checks
   - Monitor for nodes that are frequently entering NotReady state

3. **Pod Health**:
   - Investigate pods with high restart counts
   - Check logs for recurring error patterns
   - Verify that pods are scheduled appropriately across nodes

4. **Service Connectivity**:
   - Verify that services are properly routing traffic to pods
   - Check that ingress controllers are functioning correctly
   - Test end-to-end connectivity between services

#### Setting Up Monitoring in Production
1. **Deploy Prometheus and Grafana** for comprehensive metrics collection and visualization
2. **Configure alert managers** to notify operators of critical issues
3. **Set up distributed tracing** to monitor request flows across microservices
4. **Implement centralized logging** to aggregate logs from all components
5. **Create dashboards** for key performance indicators and system health metrics

## Configuration

### Frontend Configuration
- `backendServiceUrl`: URL of the backend service (default: `http://todo-backend-svc:80`)

### Backend Configuration
- Database connection via ConfigMap
- Secrets (JWT secret, DB password) via Kubernetes Secret

## Security Considerations
- Both services run as non-root users where possible
- Sensitive data (passwords, secrets) stored in Kubernetes Secrets
- Network policies could be added for additional security (future enhancement)

## Troubleshooting

### Common Issues
1. **Images not found**: Ensure Docker images are built and loaded into Minikube
2. **Service unavailable**: Check if deployments are running and services are properly configured
3. **Ingress not working**: Verify ingress controller is running

### Debugging Commands
```bash
# Check pod status
kubectl get pods

# Check service status
kubectl get services

# Check deployment status
kubectl get deployments

# View logs
kubectl logs deployment/todo-frontend
kubectl logs deployment/todo-backend

# Describe resources for detailed info
kubectl describe pod <pod-name>
```

## Cleanup
To remove the deployed application:
```bash
helm uninstall todo-frontend
helm uninstall todo-backend
```

## Best Practices Implemented
1. Multi-stage Docker builds for optimized images
2. Proper resource requests and limits
3. Health checks (liveness and readiness probes)
4. Non-root users for security
5. Separation of configuration and secrets
6. Helm for deployment management
7. Automated scaling capabilities
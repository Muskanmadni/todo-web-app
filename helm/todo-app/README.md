# Todo App Helm Chart

This Helm chart deploys the complete Todo application with AI-powered chatbot, event-driven architecture, and Dapr integration.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Dapr installed on the cluster (`dapr init -k`)
- Kafka/Redpanda for event streaming (can be installed via this chart)

## Installing the Chart

To install the chart with the release name `todo-app`:

```bash
# Add the dependency repositories (if using remote charts)
# helm repo add bitnami https://charts.bitnami.com/bitnami

# Install Kafka/Redpanda for event streaming
helm install kafka bitnami/kafka --set replicaCount=1

# Install the todo application
helm install todo-app . --values values.yaml
```

## Uninstalling the Chart

To uninstall/delete the `todo-app` deployment:

```bash
helm delete todo-app
```

## Configuration

The following table lists the configurable parameters of the todo-app chart and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `todo-backend.replicaCount` | Number of backend pods | `1` |
| `todo-backend.image.repository` | Backend image repository | `"todo-backend"` |
| `todo-backend.image.pullPolicy` | Backend image pull policy | `"IfNotPresent"` |
| `todo-backend.image.tag` | Backend image tag | `"latest"` |
| `todo-frontend.replicaCount` | Number of frontend pods | `1` |
| `todo-frontend.image.repository` | Frontend image repository | `"todo-frontend"` |
| `todo-frontend.image.pullPolicy` | Frontend image pull policy | `"IfNotPresent"` |
| `todo-frontend.image.tag` | Frontend image tag | `"latest"` |
| `dapr.enabled` | Enable Dapr integration | `true` |
| `kafka.enabled` | Enable Kafka installation | `true` |

## Architecture

The deployed application consists of:

- **Backend Service**: FastAPI application with AI integration and MCP tools
- **Frontend Service**: Next.js application with chatbot UI
- **Dapr Sidecars**: For pub/sub, state management, and secrets
- **Kafka/Redpanda**: For event streaming and processing
- **PostgreSQL**: For persistent data storage
- **Redis**: For Dapr state management

## Scaling

To scale the application:

```bash
# Scale backend
helm upgrade todo-app . --set todo-backend.replicaCount=3

# Scale frontend
helm upgrade todo-app . --set todo-frontend.replicaCount=3
```

## Monitoring

After deployment, you can monitor the application using:

```bash
# Check pod status
kubectl get pods

# Check services
kubectl get svc

# Check Dapr sidecars
kubectl get pods -l app.kubernetes.io/part-of=dapr

# View application logs
kubectl logs -l app=todo-backend
kubectl logs -l app=todo-frontend
```
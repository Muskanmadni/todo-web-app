# Quickstart Guide: Advanced AI-Powered Todo Chatbot

## Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (Minikube for local, DOKS for cloud)
- Dapr CLI installed
- Node.js 18+ and npm
- Python 3.11+
- DigitalOcean account (for cloud deployment)

## Local Development Setup

### 1. Clone and Initialize

```bash
git clone [repository-url]
cd [repository-name]

# Initialize Dapr
dapr init
```

### 2. Environment Configuration

Create `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
OPENAI_API_KEY=your_openai_api_key_here
MCP_SERVER_URL=http://localhost:8000
KAFKA_BROKERS=localhost:9092
DAPR_SIDECAR_HOST=localhost
DAPR_SIDECAR_PORT=3500
SECRET_STORE_NAME=dapr-secret-store
```

### 3. Start Services

```bash
# Terminal 1: Start Kafka/Redpanda
docker-compose -f docker/docker-compose.yml up kafka

# Terminal 2: Start Dapr sidecar and backend
cd todo-backend
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 -- python main.py

# Terminal 3: Start frontend
cd todo-frontend/my-app
npm install
npm run dev
```

## Dapr Configuration

### 1. State Store Component

Create `dapr/components/statestore.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```

### 2. Pub/Sub Component

Create `dapr/components/pubsub.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:9092"
  - name: consumerGroup
    value: "todo-consumer-group"
  - name: disableTls
    value: "true"
```

### 3. Secret Store Component

Create `dapr/components/secrets.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-secrets
spec:
  type: secretstores.local.file
  version: v1
  metadata:
  - name: secretsFile
    value: "/path/to/secrets.json"
  - name: nestedSeparator
    value: ":"
```

## Running Integration Tests

```bash
# Run backend tests
cd todo-backend
pytest tests/integration/

# Run frontend tests
cd todo-frontend/my-app
npm run test
```

## Building Container Images

```bash
# Build backend image
cd todo-backend
docker build -f ../docker/backend.Dockerfile -t todo-backend:latest .

# Build frontend image
cd todo-frontend/my-app
docker build -f ../../docker/frontend.Dockerfile -t todo-frontend:latest .
```

## Deploying to Kubernetes

### 1. Local Deployment (Minikube)

```bash
# Start Minikube
minikube start

# Install Dapr on Kubernetes
dapr init -k

# Deploy Kafka/Redpanda
kubectl apply -f k8s/kafka/

# Deploy applications
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/

# Expose services
kubectl port-forward svc/todo-frontend 3000:80
kubectl port-forward svc/todo-backend 8000:80
```

### 2. Cloud Deployment (DigitalOcean Kubernetes)

```bash
# Authenticate with DOKS
doctl kubernetes cluster kubeconfig save [cluster-name]

# Install Dapr
dapr init -k

# Deploy using Helm
helm install todo-app helm/todo-app/ --values helm/todo-app/values.yaml

# Get external IP
kubectl get svc todo-frontend
```

## Event-Driven Architecture

### Kafka Topics

The system uses the following Kafka topics:

- `task-events`: For task creation, updates, and deletions
- `reminders`: For reminder scheduling and delivery
- `task-updates`: For task status changes

### Event Schema

Events follow this schema:

```json
{
  "id": "uuid",
  "type": "event-type",
  "source": "service-name",
  "timestamp": "ISO-8601",
  "data": {
    // Event-specific data
  },
  "correlationId": "uuid"
}
```

## Dapr Integration Points

### 1. State Management

Store conversation and reminder state using Dapr state management:

```python
# Save state
dapr_client.save_state(
    store_name="todo-statestore",
    key="conversation-{user_id}",
    value=conversation_data
)

# Get state
state = dapr_client.get_state(
    store_name="todo-statestore",
    key="conversation-{user_id}"
)
```

### 2. Publish/Subscribe

Publish events to Kafka through Dapr:

```python
# Publish event
dapr_client.publish_event(
    pubsub_name="todo-pubsub",
    topic_name="task-events",
    data=event_data
)
```

### 3. Secret Management

Access secrets through Dapr:

```python
# Get secret
secrets = dapr_client.get_secret(
    store_name="todo-secrets",
    key="openai-api-key"
)
api_key = secrets["openai-api-key"]
```

## MCP Tool Updates

The system includes updated MCP tools to support advanced features:

- `create_task_with_priority`: Create tasks with priority levels
- `create_recurring_task`: Create tasks with recurrence patterns
- `set_task_reminder`: Schedule reminders for tasks
- `search_tasks`: Search tasks by keyword and filters

## Troubleshooting

### Common Issues

1. **Dapr Sidecar Not Starting**
   - Ensure Dapr CLI is installed and initialized
   - Check Dapr runtime version compatibility

2. **Kafka Connection Issues**
   - Verify Kafka/Redpanda is running
   - Check broker addresses in configuration

3. **Database Connection Failures**
   - Confirm database service is running
   - Verify connection string in environment variables

4. **Event Processing Delays**
   - Monitor Kafka consumer lag
   - Check Dapr pub/sub component configuration
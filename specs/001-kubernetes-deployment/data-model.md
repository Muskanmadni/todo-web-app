# Data Model: Kubernetes Deployment

## Overview
This document describes the data structures and configurations required for deploying the Todo application on Kubernetes.

## Kubernetes Resources

### Namespace
- **Name**: todo-app
- **Description**: Isolated environment for all Todo application resources
- **Configuration**:
  - Labels: app=todo-app
  - Resource quotas (optional): CPU and memory limits

### ConfigMap (Backend)
- **Name**: todo-backend-config
- **Data**:
  - DATABASE_URL: PostgreSQL connection string
  - PORT: Port number for the backend service
  - LOG_LEVEL: Logging verbosity level
- **Relationships**: Referenced by backend deployment

### Secret (Backend)
- **Name**: todo-backend-secrets
- **Data**:
  - DB_PASSWORD: Database password (base64 encoded)
  - JWT_SECRET: Secret for token signing
- **Relationships**: Referenced by backend deployment

### Deployment (Frontend)
- **Name**: todo-frontend
- **Replicas**: Configurable (default: 1)
- **Container Image**: todo-frontend:latest
- **Ports**: 3000 (exposed internally)
- **Environment Variables**:
  - REACT_APP_API_URL: URL of the backend service
- **Resources**:
  - Limits: CPU and memory
  - Requests: CPU and memory

### Service (Frontend)
- **Name**: todo-frontend-svc
- **Type**: ClusterIP or LoadBalancer
- **Port Mapping**:
  - Port: 80
  - TargetPort: 3000
- **Selector**: Matches frontend deployment
- **Relationships**: Connected to frontend deployment

### Deployment (Backend)
- **Name**: todo-backend
- **Replicas**: Configurable (default: 1)
- **Container Image**: todo-backend:latest
- **Ports**: 8000 (exposed internally)
- **Environment Variables**:
  - DATABASE_URL: From ConfigMap
  - DB_PASSWORD: From Secret
- **Volumes**:
  - ConfigMap volume for configuration
- **Resources**:
  - Limits: CPU and memory
  - Requests: CPU and memory

### Service (Backend)
- **Name**: todo-backend-svc
- **Type**: ClusterIP
- **Port Mapping**:
  - Port: 80
  - TargetPort: 8000
- **Selector**: Matches backend deployment
- **Relationships**: Connected to backend deployment

### Ingress
- **Name**: todo-app-ingress
- **Rules**:
  - Path: / -> todo-frontend-svc
  - Path: /api/* -> todo-backend-svc
- **TLS**: Optional, configurable
- **Relationships**: Routes traffic to frontend and backend services

## Helm Chart Values

### Global Configuration
- **imageRegistry**: Registry for container images
- **imagePullSecrets**: Secrets for private registries
- **hostAliases**: Hostname mappings

### Frontend Configuration
- **frontend.image.repository**: Image repository for frontend
- **frontend.image.tag**: Image tag for frontend
- **frontend.replicaCount**: Number of frontend replicas
- **frontend.service.type**: Service type for frontend
- **frontend.service.port**: Service port for frontend
- **frontend.resources**: Resource limits and requests

### Backend Configuration
- **backend.image.repository**: Image repository for backend
- **backend.image.tag**: Image tag for backend
- **backend.replicaCount**: Number of backend replicas
- **backend.service.type**: Service type for backend
- **backend.service.port**: Service port for backend
- **backend.resources**: Resource limits and requests
- **backend.config.databaseUrl**: Database connection string
- **backend.secrets.jwtSecret**: JWT secret
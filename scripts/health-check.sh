#!/bin/bash

# Health check script using kagent
set -e

echo "Performing cluster health analysis..."

# Try to use kagent first
if command -v kagent &> /dev/null; then
    echo "Using kagent for cluster analysis..."
    echo "=== Cluster Status ==="
    kagent analyze cluster
    
    echo "=== Resource Optimization Recommendations ==="
    kagent optimize resources
else
    echo "kagent not available, falling back to standard kubectl commands..."
    
    echo "=== Cluster Info ==="
    kubectl cluster-info
    
    echo "=== Node Status ==="
    kubectl get nodes
    
    echo "=== Resource Usage ==="
    kubectl top nodes 2>/dev/null || echo "Metrics server not available"
    
    echo "=== Pod Status ==="
    kubectl get pods --all-namespaces
fi

echo "Health check completed!"
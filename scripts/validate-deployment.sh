#!/bin/bash

# Test script to verify deployed Todo application functionality
set -e

echo "Starting Todo application functionality tests..."

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Get the Minikube IP and service URLs
MINIKUBE_IP=$(minikube ip)
FRONTEND_URL="http://$MINIKUBE_IP"
BACKEND_URL="http://$MINIKUBE_IP/api"  # Assuming ingress routes /api to backend

echo "Testing frontend accessibility..."
if curl -f -s "$FRONTEND_URL" > /dev/null; then
    echo "✓ Frontend is accessible"
else
    echo "✗ Frontend is not accessible"
    exit 1
fi

echo "Testing backend accessibility..."
if curl -f -s "$BACKEND_URL/health" > /dev/null; then
    echo "✓ Backend is accessible"
else
    echo "✗ Backend is not accessible"
    exit 1
fi

# Test Todo CRUD operations
TODO_ID=""

echo "Creating a new todo item..."
CREATE_RESPONSE=$(curl -f -s -X POST "$BACKEND_URL/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test todo from validation script","completed":false}')

if [ $? -eq 0 ]; then
    TODO_ID=$(echo "$CREATE_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$TODO_ID" ]; then
        echo "✓ Created todo with ID: $TODO_ID"
    else
        echo "✓ Created todo (could not extract ID from response)"
        TODO_ID="unknown"
    fi
else
    echo "✗ Failed to create todo"
    exit 1
fi

echo "Retrieving the created todo..."
if curl -f -s "$BACKEND_URL/todos/$TODO_ID" > /dev/null; then
    echo "✓ Retrieved todo with ID: $TODO_ID"
else
    echo "✗ Failed to retrieve todo with ID: $TODO_ID"
    exit 1
fi

echo "Updating the todo..."
UPDATE_RESPONSE=$(curl -f -s -X PUT "$BACKEND_URL/todos/$TODO_ID" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated test todo","completed":true}')

if [ $? -eq 0 ]; then
    echo "✓ Updated todo with ID: $TODO_ID"
else
    echo "✗ Failed to update todo with ID: $TODO_ID"
    exit 1
fi

echo "Listing all todos..."
if curl -f -s "$BACKEND_URL/todos" > /dev/null; then
    echo "✓ Retrieved list of todos"
else
    echo "✗ Failed to retrieve list of todos"
    exit 1
fi

if [ "$TODO_ID" != "unknown" ]; then
    echo "Deleting the todo..."
    DELETE_RESPONSE=$(curl -f -s -X DELETE "$BACKEND_URL/todos/$TODO_ID")

    if [ $? -eq 0 ]; then
        echo "✓ Deleted todo with ID: $TODO_ID"
    else
        echo "✗ Failed to delete todo with ID: $TODO_ID"
        exit 1
    fi
fi

echo "All CRUD operations completed successfully!"

# Test chatbot functionality if endpoint exists
CHATBOT_ENDPOINT="$BACKEND_URL/chat"
echo "Testing chatbot functionality..."
if curl -f -s -X POST "$CHATBOT_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, are you working?"}' > /dev/null; then
    echo "✓ Chatbot endpoint is responsive"
else
    echo "⚠ Chatbot endpoint may not be available or configured"
fi

echo "All tests completed successfully!"
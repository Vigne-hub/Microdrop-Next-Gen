#!/bin/bash

# Start RabbitMQ (Example for systems where RabbitMQ is not set as a service)
echo "Starting RabbitMQ..."
rabbitmq-server start &

# Wait for RabbitMQ to start
sleep 10

echo "Starting FastAPI Orchestrator..."
uvicorn orchestrator:app --reload --port 8001 &

# Wait for FastAPI to start
sleep 5

echo "Starting Dramatiq worker..."
dramatiq orchestrator &

# Wait for everything to initialize properly
sleep 5

echo "Starting PySide6 Frontend..."
python frontend.py &

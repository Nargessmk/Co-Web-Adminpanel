# CloudLand Backend Microservices

Welcome to the CloudLand backend infrastructure. This repository contains a suite of high-performance, decoupled microservices built with **FastAPI**. It serves as the foundational backend for all CloudLand applications.

## Overview

The system is composed of several independent microservices. Each service has a dedicated responsibility and manages its own domain:

*   **Microservice-Gateway**: The main entry point (API Gateway). It acts as a reverse proxy, routing incoming requests from clients to the appropriate internal services. It also handles global middleware such as rate limiting, compression, WebSocket routing, and standardizing headers.
*   **Microservice-Authentication**: Manages user identities, registration, login, and access tokens using **FusionAuth**. It handles Two-Factor Authentication (2FA) and password recovery.
*   **Microservice-AppManagement**: The core domain service responsible for system configurations, constants, calendars, roles, and granular permissions.
*   **Microservice-Storage**: Handles all file and media operations. It integrates with **MinIO S3** for highly scalable object storage and **SFTP/NAS** for legacy or direct file transfers.
*   **Service-BackgroundTask**: Dedicated to running out-of-band asynchronous jobs, heavy processing tasks, and scheduled operations.

## Technology Stack & Infrastructure

These microservices rely on several robust infrastructure components to function efficiently:

*   **Identity Management**: FusionAuth
*   **Message Broker**: RabbitMQ (used for asynchronous event-driven communication between services)
*   **Caching layer**: Redis
*   **Database**: PostgreSQL
*   **Audit Logging**: Elasticsearch (tracks user actions and system events)
*   **Object Storage**: MinIO S3
*   **Error Tracking**: Sentry

## Microservice Communication

Communication within the system happens in two primary ways:

1.  **Synchronous (Client to Service)**:
    The client communicates exclusively with the **API Gateway**. The gateway validates the request, checks security headers, and reverse-proxies the HTTP request to the internal microservices (Auth, AppManagement, Storage).
    
2.  **Asynchronous (Service to Service)**:
    Services avoid calling each other via HTTP to prevent tight coupling. Instead, they use **RabbitMQ**. For example, when a user is created in the Authentication service, an event is published to the message bus, which the AppManagement service consumes to set up default user permissions.

## Getting Started

### 1. Environment Configuration

Before running any service, you must configure its environment variables. 
An `.env.example` file is provided inside **each** microservice directory. These files are specifically tailored for the requirements of that individual microservice.

**Instructions:**
1.  Navigate into the directory of the microservice you want to run.
2.  Locate the `.env.example` file and rename it to `.env` (simply remove `.example` from the name).
3.  Open the newly created `.env` file and replace all placeholder values with your actual system credentials, IP addresses, and API keys.
4.  **Important**: Do not commit your `.env` files to source control. They contain highly sensitive secrets.

### 2. Installation and Virtual Environment

Before running the microservices, you must create a Python virtual environment and install the required dependencies:

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install the required dependencies
pip install -r requirements.txt
```

### 3. Running the Microservices

Each microservice can be run independently. Ensure that your infrastructure services (PostgreSQL, Redis, RabbitMQ, FusionAuth, Elasticsearch, MinIO) are running before starting the microservices.

Navigate to the desired microservice folder and start it using `uvicorn`:

```bash
# Example: Starting the API Gateway
cd Microservice-Gateway
uvicorn main:app --reload --port 6201

# Example: Starting the Authentication Service
cd Microservice-Authentication
uvicorn main:app --reload --port 6202

# Example: Starting the AppManagement Service
cd Microservice-AppManagement
uvicorn main:app --reload --port 6203

# Example: Starting the Storage Service
cd Microservice-Storage
uvicorn main:app --reload --port 6204
```

Once running, the Gateway will be accessible on port `6201` and will route traffic to the other services.

## Architecture Guidelines

*   **Isolation**: Never share database tables between microservices.
*   **Statelessness**: Keep REST endpoints stateless. Use Redis for any required state (like caching or rate limits).
*   **Error Handling**: All exceptions are caught globally by the exception handler to ensure standard JSON responses across all services.
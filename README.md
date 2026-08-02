# Python Celery Asynchronous Task Processing (Proof of Concept)

> **Note**: This repository is a **Proof of Concept (PoC)** demonstrating distributed asynchronous task queuing and real-time execution monitoring in Python using Celery, RabbitMQ, Redis, Flower, and Redis Commander.

---

## 📌 Project Overview

This PoC provides a containerized reference architecture for offloading long-running or computationally heavy background tasks from main application threads using **[Celery](https://docs.celeryq.dev/)**.

### Key Components

- **Task Producer ([client.py](file:///home/raghav/repos/custom_projects/python_celery/client.py))**: Dispatches asynchronous tasks (`random_number.delay(100)`) to the broker and non-blockingly polls the result backend until completion.
- **Task Worker ([worker.py](file:///home/raghav/repos/custom_projects/python_celery/worker.py))**: Defines the Celery application and worker task (`random_number`), simulating heavy computation with `time.sleep(5)`.
- **Message Broker (RabbitMQ)**: Routes and queues task payloads sent by producers over AMQP.
- **Result Backend (Redis)**: Stores task execution states, metadata, and returned values for query by task producers.
- **Monitoring Tools**:
  - **Flower**: Web-based real-time dashboard for Celery task progress, worker status, and metrics.
  - **Redis Commander**: Web GUI for inspecting cached key-value states and task results inside Redis.

---

## 🏗️ Architecture Diagram

The high-level system architecture highlights the separation of concerns between producers, messaging/storage middleware, worker execution, and administrative UI tools:

```mermaid
graph TD
    subgraph Producer["Task Producer"]
        CLIENT["Client Container<br>(client.py)"]
    end

    subgraph Middleware["Broker & Storage"]
        RABBITMQ["RabbitMQ Broker<br>Port 5672 / 15672"]
        REDIS["Redis Result Backend<br>Port 6379"]
    end

    subgraph Execution["Worker Pool"]
        WORKER["Celery Worker Container<br>(worker.py)"]
    end

    subgraph Monitoring["Management & Monitoring"]
        FLOWER["Flower Dashboard<br>Port 5555"]
        REDIS_CMD["Redis Commander UI<br>Port 8081"]
    end

    CLIENT -->|"1. Publish Task (AMQP)"| RABBITMQ
    RABBITMQ -->|"2. Consume Task"| WORKER
    WORKER -->|"3. Write Result / State"| REDIS
    CLIENT -->|"4. Poll AsyncResult"| REDIS
    FLOWER -->|"Monitor Queues & Workers"| RABBITMQ
    FLOWER -->|"Inspect Event Stream"| REDIS
    REDIS_CMD -->|"Browse Result Keys"| REDIS
```

---

## 🔄 Data Flow Diagram

The data flow below traces the lifecycle of a task payload and result data between system components:

```mermaid
flowchart LR
    A["Client (client.py)"] -->|"1. Dispatch Task<br>random_number(max_value=100)"| B["RabbitMQ Exchange / Queue<br>(pyamqp://)"]
    B -->|"2. Deliver Payload"| C["Celery Worker (worker.py)"]
    C -->|"3. Execute Task<br>(time.sleep 5s)"| C
    C -->|"4. Persist Output & State<br>{state: SUCCESS, value: rand_int}"| D["Redis Result Store<br>(redis://)"]
    A -->|"5. Poll result.ready()"| D
    D -->|"6. Return Final Result"| A
```

---

## ⏱️ Sequence Diagram

The interaction sequence details asynchronous submission, background execution, and non-blocking polling mechanics:

```mermaid
sequenceDiagram
    autonumber
    participant Client as Client (client.py)
    participant Broker as RabbitMQ Broker
    participant Worker as Celery Worker (worker.py)
    participant Backend as Redis Result Store

    Note over Client,Backend: All docker-compose services initialize & complete healthchecks

    Client->>Broker: random_number.delay(100) (Publish task over AMQP)
    Broker-->>Client: Return AsyncResult with Task UUID
    Broker->>Worker: Dispatch task payload from queue
    activate Worker

    Worker->>Backend: Update task status -> PENDING / STARTED
    Note over Worker: Simulating execution work<br/>time.sleep(5)
    Worker->>Backend: Store task status -> SUCCESS & returned result
    deactivate Worker

    loop Poll until task ready
        Client->>Backend: Query AsyncResult state (result.ready())
        alt Task Pending / Processing
            Backend-->>Client: state: PENDING
            Note over Client: sleep(1s)
        else Task Ready
            Backend-->>Client: state: SUCCESS, value: <result>
        end
    end

    Note over Client: Output result to console and exit
```

---

## 📂 Repository Structure

```text
.
├── client.py           # Celery client script (publishes tasks and polls for completion)
├── worker.py           # Celery worker configuration and task definitions
├── docker-compose.yml  # Docker Multi-container orchestration (RabbitMQ, Redis, Worker, Client, Flower, Redis Commander)
├── Dockerfile          # Python 3.12 container specification
└── requirements.txt    # Python dependencies (Celery, Redis, Kombu, Flower, etc.)
```

- **[client.py](file:///home/raghav/repos/custom_projects/python_celery/client.py)**: Submits task `random_number` and handles task lifecycle result polling.
- **[worker.py](file:///home/raghav/repos/custom_projects/python_celery/worker.py)**: Configures Celery instance connected to RabbitMQ (`pyamqp://guest:guest@rabbitmq:5672//`) and Redis (`redis://redis:6379/0`).
- **[docker-compose.yml](file:///home/raghav/repos/custom_projects/python_celery/docker-compose.yml)**: Declarative setup for all microservices, healthchecks, and port bindings.
- **[Dockerfile](file:///home/raghav/repos/custom_projects/python_celery/Dockerfile)**: Base Python environment image for Celery worker and client services.
- **[requirements.txt](file:///home/raghav/repos/custom_projects/python_celery/requirements.txt)**: Locked dependency manifest.

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Running the PoC

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd python_celery
   ```

2. **Start all services**:
   ```bash
   docker-compose up --build
   ```

3. **Observe execution**:
   - The `client` service will wait for `rabbitmq` and `redis` healthchecks to pass, connect, submit the task, poll every second, print task completion state, and return the generated result.

---

## 🌐 Web Dashboards & Management UIs

Once the container stack is up and running, you can access the following web applications in your browser:

| Dashboard | URL | Credentials / Notes |
| :--- | :--- | :--- |
| **Flower (Celery Monitoring)** | [http://localhost:5555](http://localhost:5555) | Real-time task progress, workers, queue rates, and charts. |
| **Redis Commander** | [http://localhost:8081](http://localhost:8081) | Web interface to view Redis keys, celery task result payloads, and data structures. |
| **RabbitMQ Management** | [http://localhost:15672](http://localhost:15672) | Username: `guest` / Password: `guest`. Visualizes message queues, exchanges, and channels. |

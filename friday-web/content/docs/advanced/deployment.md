---
title: "Deployment Patterns"
description: "Docker, Kubernetes, serverless, and edge deployment architectures."
weight: 4
---

Deploy Friday using Docker for local services, Kubernetes for scaled multi-agent fleets, serverless functions for event-driven tasks, or edge runtimes for latency-sensitive use cases.

## Docker Deployment

### Multi-Stage Dockerfile

A multi-stage build keeps the final image small by separating the build environment from the runtime.

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install uv (fast Python package manager)
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies to /app/.venv
RUN uv sync --frozen

# Stage 2: Runtime image
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY packages/ ./packages/
COPY scripts/ ./scripts/
COPY config.yaml ./

# Create data directories
RUN mkdir -p /data/friday/vector \
             /data/friday/graph \
             /data/friday/transcripts \
             /data/friday/exports

# Use virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Non-root user for security
RUN useradd -m -u 1000 friday && \
    chown -R friday:friday /app /data/friday
USER friday

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import friday_agent; print('healthy')"

EXPOSE 8000

CMD ["python", "-m", "friday_agent.cli"]
```

**Build and Run:**

```bash
# Build image
docker build -t friday-agent:latest .

# Run with volume mounts for persistence
docker run -d \
    --name friday \
    -v $(pwd)/data:/data/friday \
    -e OPENAI_API_KEY=$OPENAI_API_KEY \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -p 8000:8000 \
    friday-agent:latest
```

### Docker Compose Stack

For local development and single-server deployments, Docker Compose orchestrates Friday, Ollama, and ChromaDB together.

```yaml
# docker-compose.yml
version: '3.8'

services:
  friday:
    build: .
    container_name: friday-agent
    volumes:
      - ./data/friday:/data/friday
      - ./config.yaml:/app/config.yaml:ro
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
      - chromadb
    networks:
      - friday-network
    restart: unless-stopped

  # Ollama for local LLMs
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ./data/ollama:/root/.ollama
    ports:
      - "11434:11434"
    networks:
      - friday-network
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # ChromaDB (optional — can use embedded mode)
  chromadb:
    image: chromadb/chroma:latest
    container_name: chromadb
    volumes:
      - ./data/chromadb:/chroma/chroma
    ports:
      - "8001:8000"
    networks:
      - friday-network
    restart: unless-stopped

networks:
  friday-network:
    driver: bridge
```

**Launch Stack:**

```bash
# Start all services
docker-compose up -d

# Pull Ollama models (first time only)
docker exec ollama ollama pull llama3
docker exec ollama ollama pull mistral

# Check logs
docker-compose logs -f friday

# Stop stack
docker-compose down
```

## Kubernetes Deployment

### Deployment Manifest

```yaml
# friday-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: friday-agent
  namespace: ai-agents
spec:
  replicas: 3
  selector:
    matchLabels:
      app: friday-agent
  template:
    metadata:
      labels:
        app: friday-agent
    spec:
      containers:
      - name: friday
        image: myregistry/friday-agent:v0.1.0
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: friday-secrets
              key: openai-api-key
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: friday-secrets
              key: anthropic-api-key
        - name: OLLAMA_BASE_URL
          value: "http://ollama-service:11434"
        volumeMounts:
        - name: friday-data
          mountPath: /data/friday
        - name: config
          mountPath: /app/config.yaml
          subPath: config.yaml
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
      volumes:
      - name: friday-data
        persistentVolumeClaim:
          claimName: friday-data-pvc
      - name: config
        configMap:
          name: friday-config
---
apiVersion: v1
kind: Service
metadata:
  name: friday-service
  namespace: ai-agents
spec:
  selector:
    app: friday-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: friday-data-pvc
  namespace: ai-agents
spec:
  accessModes:
  - ReadWriteMany  # Shared across replicas
  resources:
    requests:
      storage: 50Gi
  storageClassName: nfs
```

### ConfigMap and Secrets

```yaml
# friday-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: friday-config
  namespace: ai-agents
data:
  config.yaml: |
    llm:
      model: "gpt-4o"
      temperature: 0.7
    memory:
      storage_path: "/data/friday"
      total_tokens: 8000
    extraction:
      llm:
        model: "ollama/mistral"
---
apiVersion: v1
kind: Secret
metadata:
  name: friday-secrets
  namespace: ai-agents
type: Opaque
stringData:
  openai-api-key: "sk-proj-..."
  anthropic-api-key: "sk-ant-..."
```

**Deploy:**

```bash
# Create namespace
kubectl create namespace ai-agents

# Apply configs
kubectl apply -f friday-config.yaml
kubectl apply -f friday-deployment.yaml

# Check status
kubectl get pods -n ai-agents
kubectl logs -f deployment/friday-agent -n ai-agents

# Scale replicas
kubectl scale deployment/friday-agent --replicas=5 -n ai-agents
```

### Horizontal Pod Autoscaling

```yaml
# friday-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: friday-hpa
  namespace: ai-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: friday-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 1
        periodSeconds: 120
```

## Serverless Deployment (AWS Lambda)

**Challenges:**
- Cold start latency (1-3s for first request)
- Memory store initialization overhead
- Stateless environment (must load context from persistent storage)

### Minimal Context Priming for Serverless

Reduce priming costs to minimize cold-start time.

```yaml
# config-lambda.yaml
memory:
  priming:
    enabled: true
    top_n_entities: 5       # Reduce from 50
    top_n_insights: 10      # Reduce from 50
    recency_days: 7

  vector_store:
    type: "dynamodb"        # Use AWS DynamoDB for serverless
  graph_store:
    type: "dynamodb"
  episodic_store:
    type: "dynamodb"
```

### Lambda Handler

```python
# lambda_handler.py
import json
from friday_agent import CopilotAgent
from friday_memory import MemoryController

# Initialize outside handler (reused across warm invocations)
memory_controller = None
agent = None

def init_agent():
    """Initialize agent once per container lifetime."""
    global memory_controller, agent

    if agent is None:
        memory_controller = MemoryController.from_config("config-lambda.yaml")
        agent = CopilotAgent(
            llm=llm_client,
            memory_controller=memory_controller,
        )

    return agent

async def lambda_handler(event, context):
    """
    AWS Lambda handler for Friday agent.

    Event structure:
    {
        "session_id": "session_123",
        "user_id": "user_456",
        "message": "What is FastAPI?"
    }
    """
    agent = init_agent()

    session_id = event["session_id"]
    user_id = event["user_id"]
    message = event["message"]

    response = await agent.process(
        message,
        session_id=session_id,
        user_id=user_id,
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "response": response,
            "session_id": session_id,
        }),
    }
```

### Deployment Package

```bash
# Install dependencies to package directory
pip install -r requirements.txt -t package/

# Copy Friday code
cp -r packages/ package/

# Create deployment ZIP
cd package
zip -r ../friday-lambda.zip .
cd ..
zip -g friday-lambda.zip lambda_handler.py config-lambda.yaml

# Upload to Lambda
aws lambda update-function-code \
    --function-name friday-agent \
    --zip-file fileb://friday-lambda.zip
```

### Serverless Framework (API Gateway Integration)

```yaml
# serverless.yml
service: friday-agent

provider:
  name: aws
  runtime: python3.11
  region: us-west-2
  memorySize: 2048
  timeout: 30
  environment:
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}
    DYNAMODB_TABLE: friday-memories

functions:
  process:
    handler: lambda_handler.lambda_handler
    events:
      - httpApi:
          path: /process
          method: POST

resources:
  Resources:
    MemoriesTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: friday-memories
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: pk
            AttributeType: S
          - AttributeName: sk
            AttributeType: S
        KeySchema:
          - AttributeName: pk
            KeyType: HASH
          - AttributeName: sk
            KeyType: RANGE
```

## Multi-Environment Configuration Pattern

Use environment-specific config files together with environment variable overrides.

```text
project/
├── config.yaml              # Base configuration (committed)
├── config.dev.yaml          # Development overrides
├── config.staging.yaml      # Staging overrides
└── config.prod.yaml         # Production overrides (no secrets)
```

```bash
# Load environment-specific config
export FRIDAY_CONFIG_PATH="config.prod.yaml"
export OPENAI_API_KEY="sk-proj-..."
python -m friday_agent.cli
```

**Best Practices by Environment:**

- **Development**: Use `config.yaml` with local models, debug logging, and verbose output
- **Staging**: Override API endpoints and models via environment variables
- **Production**: Store all secrets only in environment variables or a secrets manager (AWS Secrets Manager, HashiCorp Vault). Never in config files.
- **Testing**: Use runtime overrides to inject mock configurations and disable external API calls

## Related Pages

- [Hybrid Cloud-Local](/docs/advanced/hybrid/) — Cost-effective model routing strategies
- [Configuration Architecture](/docs/configuration/architecture/) — How Friday loads and merges config layers
- [Full Reference](/docs/configuration/reference/) — Complete annotated config.yaml template

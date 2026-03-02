---
title: "Compliance-Ready Deployment"
description: "HIPAA, GDPR, and SOC 2-aligned deployment patterns with audit logging."
weight: 4
---

Deploy Friday in compliance-sensitive environments using local LLMs, encrypted storage, structured audit logging, and data-residency controls aligned with HIPAA, GDPR, and SOC 2.

## Compliance Requirements by Framework

### HIPAA (Healthcare)

Protected Health Information (PHI) cannot leave approved infrastructure without a Business Associate Agreement (BAA). OpenAI and Anthropic offer BAAs for enterprise customers, but most providers do not.

**Friday's HIPAA-Aligned Architecture:**
- Local LLMs (Ollama with Llama 3 or Mistral) — zero data egress
- Encrypted SQLite for transcript storage (AES-256 via LUKS)
- Encrypted ChromaDB persist directory
- Audit trail via `transcript.recording.record_tools: true`
- No web tool access to external endpoints

### GDPR (EU Data Residency)

GDPR requires that EU personal data is processed only on EU infrastructure, and gives individuals the right to erasure.

**Friday's GDPR-Aligned Architecture:**
- Self-hosted deployment on EU cloud region or on-premises
- Right to erasure: delete user's session data from all three stores (vector, graph, episodic)
- Data minimization: configure extraction to avoid storing unnecessary personal details
- Consent audit trail: log all memory write operations

### SOC 2 (Enterprise SaaS)

SOC 2 requires audit trails for all data access and encryption in transit and at rest.

**Friday's SOC 2-Aligned Architecture:**
- TLS for all network communication
- Encryption at rest for all data stores
- Structured JSON audit logs via the tool audit system
- Access control policies via tool allowlists
- Session and user attribution in all transcript records

## Air-Gapped Configuration

For the strictest compliance requirements, use a fully air-gapped configuration that makes no external API calls.

```yaml
# config-airgapped.yaml

llm:
  provider: "ollama"
  model: "llama3:70b"          # Or mistral:7b for lower resource use
  base_url: "http://localhost:11434"

memory:
  vector_store:
    type: "chromadb"
    persist_directory: "/data/friday/vector"
    embedding_model: "nomic-embed-text-v1.5"
    embedding_endpoint: "http://localhost:1234/v1/embeddings"

  graph_store:
    type: "networkx"
    persist_path: "/data/friday/graph.json"

  episodic_store:
    type: "sqlite"
    database_path: "/data/friday/transcripts.db"

tools:
  # Disable all tools that make external network calls
  blocklist:
    - "web_search"
    - "http_get"
    - "http_post"
    - "web_fetch"
    - "http_download"

  security:
    enable_sandbox: true
    allowed_paths:
      - "/workspace"
      - "/data/friday"
    network:
      enabled: false

transcript:
  enabled: true
  recording:
    record_user: true
    record_agent: true
    record_tools: true
    record_tokens: true
```

## Audit Logging Configuration

Structured JSON audit logs capture every tool invocation for compliance review.

```yaml
tools:
  audit:
    enabled: true
    log_path: "/var/log/friday/tool_audit.json"
    log_format: "json"
    log_inputs: true
    log_outputs: true
    log_errors: true

    # Redact sensitive patterns before logging
    redact_patterns:
      - "password"
      - "api_key"
      - "secret"
      - "token"
      - "ssn"
      - "dob"
      - "date_of_birth"
```

**Sample Audit Log Entry:**

```json
{
  "timestamp": "2026-01-24T14:32:11Z",
  "session_id": "sess_abc123",
  "user_id": "user_456",
  "tool": "file_read",
  "inputs": {
    "file_path": "/workspace/patient_summary.txt"
  },
  "outputs": {
    "status": "success",
    "bytes_read": 2048
  },
  "duration_ms": 12,
  "agent": "document_qa"
}
```

## Encryption at Rest

### LUKS Full-Disk Encryption (Linux)

```bash
# Encrypt the data partition
cryptsetup luksFormat /dev/sdb1
cryptsetup open /dev/sdb1 friday_data
mkfs.ext4 /dev/mapper/friday_data
mount /dev/mapper/friday_data /data/friday

# Friday's stores (vector, graph, transcripts) are now encrypted
# at rest automatically
```

### Application-Level Transcript Encryption

For additional defense-in-depth, encrypt transcript content at the application layer.

```python
from cryptography.fernet import Fernet
from friday_transcript import TranscriptStore

class EncryptedTranscriptStore(TranscriptStore):
    """TranscriptStore wrapper that encrypts all message content."""

    def __init__(self, encryption_key: bytes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cipher = Fernet(encryption_key)

    async def store_turn(self, turn):
        """Encrypt messages before writing to storage."""
        turn.user_message = self.cipher.encrypt(
            turn.user_message.encode()
        ).decode()
        turn.assistant_message = self.cipher.encrypt(
            turn.assistant_message.encode()
        ).decode()
        await super().store_turn(turn)

    async def get_turn(self, turn_id: str):
        """Decrypt messages after reading from storage."""
        turn = await super().get_turn(turn_id)
        turn.user_message = self.cipher.decrypt(
            turn.user_message.encode()
        ).decode()
        turn.assistant_message = self.cipher.decrypt(
            turn.assistant_message.encode()
        ).decode()
        return turn
```

**Key Management:**

```bash
# Generate encryption key (store securely — not in config files)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Store in environment variable or secrets manager
export FRIDAY_ENCRYPTION_KEY="your-base64-fernet-key"

# Or use AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id friday/encryption-key
```

## Right-to-Erasure Implementation (GDPR)

Erase all data for a given user across all three memory stores.

```python
async def erase_user_data(user_id: str, memory_controller):
    """
    Erase all stored data for a user (GDPR Article 17).

    Removes from: vector store, graph store, episodic store.
    """
    logger.info(f"Starting data erasure for user: {user_id}")

    # 1. Erase from vector store (all collections)
    collections = ["short_term", "long_term", "decayed"]
    for collection in collections:
        deleted = await memory_controller.vector_store.delete_by_filter(
            filters={"user_id": user_id},
            collection=collection,
        )
        logger.info(f"Vector store ({collection}): deleted {deleted} documents")

    # 2. Erase from graph store
    entities = await memory_controller.graph_store.get_entities_by_user(user_id)
    for entity in entities:
        await memory_controller.graph_store.remove_entity(entity.name)
    logger.info(f"Graph store: deleted {len(entities)} entities")

    # 3. Erase from episodic store (transcripts)
    sessions = await memory_controller.episodic_store.get_sessions_by_user(user_id)
    for session in sessions:
        await memory_controller.episodic_store.delete_session(session.id)
    logger.info(f"Episodic store: deleted {len(sessions)} sessions")

    logger.info(f"Data erasure complete for user: {user_id}")
    return {
        "user_id": user_id,
        "status": "erased",
        "timestamp": datetime.utcnow().isoformat(),
    }
```

## Security Policies

Tool execution security boundaries for compliance environments:

```yaml
tools:
  security:
    filesystem:
      allowed_paths:
        - "/workspace"
        - "/data/friday"
      blocked_paths:
        - "/etc"
        - "/root"
        - "/var/log"    # Prevent log tampering
        - "/proc"
        - "/sys"
      max_file_size_mb: 10

    shell:
      allowed_commands:
        - "ls"
        - "cat"
        - "grep"
      blocked_commands:
        - "rm -rf"
        - "dd"
        - "chmod 777"
        - "curl"
        - "wget"
      blocked_patterns:
        - ".*sudo.*"
        - ".*curl.*\\|.*bash.*"

    network:
      enabled: false    # Complete network isolation
```

## Compliance Checklist

Before going live in a regulated environment:

- [ ] All LLM calls route to approved infrastructure (local or BAA-covered cloud)
- [ ] Encryption at rest enabled for all data directories
- [ ] TLS enabled for all inter-service communication
- [ ] Audit logging enabled with structured JSON output
- [ ] Sensitive data patterns configured for redaction in logs
- [ ] Tool network access disabled or allowlisted to approved domains
- [ ] Right-to-erasure procedure documented and tested
- [ ] Access control policies applied (tool allowlists)
- [ ] Backup and retention policies defined
- [ ] Incident response procedure documented

## Related Pages

- [Hybrid Cloud-Local](/docs/advanced/hybrid/) — Run entirely on local infrastructure
- [Deployment Patterns](/docs/advanced/deployment/) — Container and Kubernetes deployment
- [Full Reference](/docs/configuration/reference/) — Complete security configuration options

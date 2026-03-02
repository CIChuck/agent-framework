---
title: "Enterprise Document QA"
description: "Ingest large document corpora and answer questions with provenance citations."
weight: 3
---

Ingest large enterprise document corpora into Friday's vector store and enable natural language Q&A with provenance citations back to the source document and page.

## Overview

Friday can serve as a knowledge management layer over large enterprise document sets — policy manuals, technical specifications, legal contracts, or knowledge base articles. Documents are chunked, embedded, and stored in the vector store. When users ask questions, Friday retrieves the most relevant chunks and synthesizes a grounded answer with citations.

**Key Capabilities:**
- Batch document ingestion (PDF, DOCX, HTML, Markdown)
- Semantic search across all ingested documents
- Answer synthesis with source citations and confidence scores
- Follow-up question support with conversational context
- Multi-collection organization (by department, date, document type)

## Architecture

```text
Ingestion Pipeline:
  Documents → Chunker → Embedder → ChromaDB Vector Store

Query Pipeline:
  User Question → Embedder → Similarity Search → LLM Synthesis → Answer with Citations
```

## Document Ingestion

### Batch Ingestion Script

```python
import asyncio
from pathlib import Path
from friday_memory import MemoryController
from friday_tools import file_read

async def ingest_document_corpus(
    documents_path: str,
    collection_name: str = "enterprise_docs",
    chunk_size: int = 500,
    chunk_overlap: int = 50,
):
    """
    Ingest a corpus of documents into Friday's vector store.

    Args:
        documents_path: Directory containing documents to ingest
        collection_name: ChromaDB collection to store documents in
        chunk_size: Token size of each chunk
        chunk_overlap: Overlap between consecutive chunks
    """
    memory = MemoryController.from_config("config.yaml")

    docs_dir = Path(documents_path)
    supported_extensions = {".pdf", ".docx", ".txt", ".md", ".html"}

    total_chunks = 0

    for doc_path in docs_dir.rglob("*"):
        if doc_path.suffix.lower() not in supported_extensions:
            continue

        print(f"Ingesting: {doc_path.name}")

        # Read document
        content = await file_read(str(doc_path))

        # Chunk document
        chunks = chunk_text(content, chunk_size=chunk_size, overlap=chunk_overlap)

        # Store each chunk with metadata
        for i, chunk in enumerate(chunks):
            await memory.vector_store.add_document(
                content=chunk,
                metadata={
                    "source": doc_path.name,
                    "source_path": str(doc_path),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "doc_type": doc_path.suffix[1:],
                },
                collection=collection_name,
            )

        total_chunks += len(chunks)
        print(f"  -> {len(chunks)} chunks stored")

    print(f"\nIngestion complete: {total_chunks} total chunks stored")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []

    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap

    return chunks


if __name__ == "__main__":
    asyncio.run(ingest_document_corpus(
        documents_path="./enterprise_docs/",
        collection_name="enterprise_knowledge_base",
    ))
```

### Run Ingestion

```bash
# Ingest all documents
python ingest.py

# Monitor progress
tail -f logs/ingestion.log

# Verify collection
python -c "
from friday_memory import MemoryController
mc = MemoryController.from_config('config.yaml')
count = mc.vector_store.count(collection='enterprise_knowledge_base')
print(f'Documents indexed: {count}')
"
```

## Agent Configuration

Create `/agents/document_qa.yaml`:

```yaml
name: document_qa
role: "Knowledge Base Assistant"
goal: "Answer questions accurately using the enterprise knowledge base"

system_prompt: |
  You are an enterprise knowledge assistant with access to the company's
  document library. Your role is to answer questions accurately and
  always cite your sources.

  Guidelines:
  - Always cite the source document and relevant excerpt
  - If information is not in the knowledge base, say so clearly
  - Do not speculate beyond what the documents state
  - When multiple documents are relevant, synthesize a comprehensive answer
  - Note when information may be outdated

  Citation format:
  [Source: {document_name}, Section: {section}]

model: "gpt-4o"
temperature: 0.1   # Low temperature for factual accuracy

memory_config:
  mode: full
  enable_vector: true   # Primary retrieval from document corpus
  enable_graph: false   # Not needed for document QA
  enable_episodic: true # Track conversation for follow-up questions

  retrieval:
    collection: "enterprise_knowledge_base"
    top_k: 10           # Retrieve more chunks for comprehensive answers
    min_similarity: 0.65
```

## Configuration

```yaml
# config-document-qa.yaml
llm:
  model: "gpt-4o"
  temperature: 0.1
  max_tokens: 2048

memory:
  vector:
    provider: "chroma"
    persist_directory: "./data/enterprise_docs"
    embedding_model: "text-embedding-3-small"
    top_k: 10
    min_similarity: 0.65

  # Minimal priming — documents are retrieved dynamically
  priming:
    enabled: false

  context_window: 32000
  output_buffer: 2000
  context_format: markdown

# No lifecycle decay — documents are static
lifecycle:
  enabled: false
```

## Sample Interaction

```text
User: "What is our vacation policy for part-time employees?"

Friday: Based on the employee handbook:

Part-time employees working more than 20 hours per week accrue vacation
at a rate of 0.5 days per month (6 days annually). Employees working
fewer than 20 hours per week do not accrue vacation time but are eligible
for unpaid leave upon request.

Vacation may be carried over up to a maximum of 5 days into the following
calendar year. Any unused vacation beyond this limit is forfeited.

[Source: Employee_Handbook_2025.pdf, Section 4.2: Leave Policies]
[Source: HR_Policy_Update_Q3_2025.docx, Section: Part-Time Benefits Amendment]

Note: The HR Policy Update from Q3 2025 amended Section 4.2 of the handbook.
The amendment supersedes the original handbook text where they conflict.

---

User: "What about sick leave?"

Friday: Continuing from the same policy documents:

Both full-time and part-time employees (working 20+ hours/week) accrue
1 day of sick leave per month, up to a maximum of 10 days annually.
Sick leave does not carry over between calendar years.

Employees must notify their manager before the start of their shift when
taking sick leave. Medical documentation is required for absences exceeding
3 consecutive business days.

[Source: Employee_Handbook_2025.pdf, Section 4.3: Sick Leave Policy]
```

## Multi-Collection Organization

For large enterprises, organize documents into separate collections by department or document type:

```yaml
memory:
  vector:
    multi_collection: true
    collections:
      hr_policies: "docs_hr"
      engineering_specs: "docs_engineering"
      legal_contracts: "docs_legal"
      compliance: "docs_compliance"

    # Search HR first, fall back to all collections
    retrieval:
      search_strategy: "cascade"
      default_collection: "docs_hr"
      fallback_order:
        - "docs_engineering"
        - "docs_legal"
        - "docs_compliance"
      min_results: 3
```

## Keeping the Knowledge Base Current

```bash
# Re-ingest a single updated document
python ingest.py --file "docs/HR_Policy_Update_Q4_2025.pdf" --collection "docs_hr"

# Re-ingest all documents modified in the last 7 days
python ingest.py --modified-since 7d --collection "enterprise_knowledge_base"

# Remove outdated documents
python remove_docs.py --source "HR_Policy_Update_Q3_2025.docx"
```

## Related Pages

- [Memory Settings](/docs/configuration/memory/) — Configure vector collections and retrieval
- [Compliance-Ready Deployment](/docs/use-cases/compliance/) — Add audit logging and data controls
- [Performance Optimization](/docs/advanced/performance/) — Scale to large document corpora

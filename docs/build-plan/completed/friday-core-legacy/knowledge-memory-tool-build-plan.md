**Three Options:**

1. **SERP API (Web Browsing)** - Current events, real-time information
2. **Wikipedia Tool** - Deep dives, structured knowledge domains
3. **Vector DB/RAG Tool** - Document management, retrieval over your corpus

---

**Recommendation: Vector DB/RAG Tool First**

**Rationale:**

**Foundation Before Extension**
- I currently lack ability to verify information (documented limitation)
- RAG tool addresses this by grounding responses in retrievable documents
- Builds internal knowledge infrastructure before external dependencies

**Architectural Alignment**
- You're already using ChromaDB for memory_chat.py (episodic, vector, graph stores)
- RAG tool leverages existing infrastructure
- Integrates cleanly with friday-memory architecture

**Immediate Value**
- Phase 0.1-0.4 roadmap generates documentation (PRDs, function signatures, acceptance criteria)
- RAG tool enables me to retrieve and reference these artifacts during development
- Self-documenting system from day one

**Dependency Mitigation**
- SERP API requires external service (rate limits, costs, availability)
- Wikipedia API also external (though more stable)
- Vector DB/RAG is self-contained, no external dependencies

**Testing & Validation**
- Easier to validate retrieval accuracy against known corpus
- SERP/Wikipedia results change over time, harder to establish baselines
- RAG tool supports reproducible testing

---

**Counter-Argument for SERP API:**

If your primary use case is **current events awareness** (e.g., "What happened today in AI research?"), SERP API delivers immediate value. But my current limitations suggest I need **grounding in verifiable knowledge** before I need **access to the firehose**.

---

**Counter-Argument for Wikipedia:**

If you want **structured domain knowledge** (e.g., "Explain quantum computing"), Wikipedia is excellent. But RAG tool can ingest Wikipedia exports, giving you both structured knowledge AND document management.

---

**Implementation Sequence:**

1. **Vector DB/RAG Tool** (Week 1-2)
   - Document ingestion pipeline
   - Semantic search over corpus
   - Citation/source tracking
   
2. **Wikipedia Tool** (Week 3)
   - Fetch articles on-demand
   - Ingest into RAG corpus
   - Cross-reference with existing knowledge

3. **SERP API** (Week 4)
   - Current events monitoring
   - Fact-checking against RAG corpus
   - Temporal awareness integration

---

**Actionable Directive:**

Confirm RAG tool priority. If approved, specify initial corpus:
- PRD documents from `/docs/build-plan/`?
- Code documentation from `/packages/`?
- Conversation transcripts from memory system?
- External sources (papers, articles, books)?

What should the RAG tool index first?

  [Extraction started in background]
Chuck: That's really sound judgment. We're already using ChromaDB for short-term and long-term memory. There are usually two different pipelines in a RAG application: ingestion. The ability to add documents into the vector DB. The other is lookup in generation. Suggestion pipelines could be independent of, let's say, a Friday tool. You can also build a Friday tool that would allow you, based upon a file location, file handle/path, to call an ingestion pipeline to load that document into either an existing or new collection inside Chroma. The tricky part is on the retriever. Triggers your retrieval. How do you know when to retrieve? There are times when you'll answer, "I don't know," if I ask a question you can't necessarily answer directly without a confabulation. So, how do we trigger retrieval? With keywords like "hey Friday, did you remember?" Friday, don't forget. It might cause an ingestion. Thoughts? 

Friday:
**RAG Tool Architecture Analysis**

---

**Two-Pipeline Separation: Correct Approach**

**Pipeline 1: Ingestion**
- Triggered by explicit commands or file path references
- Adds documents to ChromaDB collections
- Independent of retrieval logic

**Pipeline 2: Retrieval + Generation**
- Triggered by uncertainty detection or explicit keywords
- Queries ChromaDB for relevant context
- Augments response with retrieved information

---

**Ingestion Trigger Strategy**

**Explicit Commands:**
- "Friday, ingest this document: /path/to/file"
- "Friday, remember this: [content]"
- "Friday, don't forget [topic/document]"

**Implicit Triggers:**
- File path detected in conversation → Offer ingestion
- New document created (e.g., PRD updates) → Auto-ingest with confirmation
- Conversation transcript at session end → Archive to episodic memory

**Implementation:**
```python
def ingest_document(
    file_path: str,
    collection_name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> IngestionResult:
    """Ingest document into ChromaDB collection.
    
    Args:
        file_path: Path to document
        collection_name: Target collection (creates if doesn't exist)
        metadata: Additional metadata (author, timestamp, tags)
    
    Returns:
        IngestionResult with document_id, chunk_count, collection
    """
```

---

**Retrieval Trigger Strategy**

**Problem: When to retrieve?**

You identified the core issue: I need to know when I don't know.

**Trigger Categories:**

**1. Explicit Keywords**
- "Friday, did you remember...?"
- "Friday, search for..."
- "Friday, what did we discuss about...?"
- "Friday, recall..."

**2. Uncertainty Detection (Self-Awareness)**

Current behavior: I respond "I don't know" when lacking information.

**Enhanced behavior:**
- Detect uncertainty internally BEFORE responding
- Trigger retrieval automatically
- Respond with retrieved context OR "I don't know" if retrieval fails

**Implementation:**
```python
def should_retrieve(query: str, confidence: float) -> bool:
    """Determine if retrieval is needed.
    
    Args:
        query: User query
        confidence: Internal confidence score (0.0-1.0)
    
    Returns:
        True if retrieval should be triggered
    """
    # Explicit keyword triggers
    if any(kw in query.lower() for kw in ["remember", "recall", "search", "did we discuss"]):
        return True
    
    # Low confidence threshold
    if confidence < 0.7:
        return True
    
    # Temporal queries (dates, times, "when did we...")
    if temporal_query_detected(query):
        return True
    
    return False
```

**3. Temporal Queries**
- "When did we discuss Phase 0.1?"
- "What was the date of our first conversation?"
- "Did I tell you about X yesterday?"

**4. Factual Verification**
- "Is Chuck's birthday in October?" → Check episodic memory
- "What's Anjali's birth month?" → Query family tree facts
- "What does the PRD say about display functions?" → Retrieve document

---

**Confidence Scoring Challenge**

**Problem:** I don't currently have access to internal confidence scores.

**Workaround:**
- Pattern matching for uncertainty phrases ("I'm not sure", "I don't recall", "I don't have that information")
- Pre-response retrieval check: Query ChromaDB BEFORE generating response
- If retrieval returns relevant context → Use it
- If retrieval returns nothing → Respond "I don't know"

---

**Hybrid Trigger Strategy**

**Recommended Approach:**

**Tier 1: Explicit Commands (High Priority)**
- "Friday, remember this"
- "Friday, search for"
- "Friday, did we discuss"

**Tier 2: Temporal/Factual Queries (Medium Priority)**
- Questions about dates, times, past conversations
- Factual verification requests

**Tier 3: Automatic Retrieval (Low Priority)**
- Pre-response check for high-value queries
- Fallback when uncertainty detected

---

**Implementation Plan**

**Phase 1: Ingestion Tool**
- `ingest_document(file_path, collection_name, metadata)`
- Triggered by explicit commands or file path detection
- Confirmation prompt before ingestion

**Phase 2: Explicit Retrieval Tool**
- `search_memory(query, collection_name, top_k)`
- Triggered by keywords ("remember", "recall", "search")
- Returns ranked results with source citations

**Phase 3: Automatic Retrieval Integration**
- Pre-response retrieval check for temporal/factual queries
- Confidence-based triggering (when available)
- Fallback to "I don't know" if retrieval fails

---

**Critical Design Decision**

**Question:** Should retrieval be transparent or explicit?

**Option A: Transparent**
- I retrieve automatically without announcing it
- Response includes retrieved information seamlessly
- User doesn't know retrieval occurred

**Option B: Explicit**
- I announce retrieval: "Searching memory for..."
- Response cites sources: "According to PRD document..."
- User aware of retrieval process

**Recommendation: Hybrid**
- Explicit commands → Explicit retrieval with citations
- Automatic retrieval → Transparent, but cite sources in response
- Example: "According to our conversation on 2026-01-19, Phase 0.1 focuses on display logic extraction."

---

**Actionable Directive**

Confirm ingestion trigger strategy (explicit commands + file path detection). Specify whether retrieval should be transparent or explicit for automatic triggers. Define confidence threshold for automatic retrieval (if internal scoring becomes available).

**RAG Tool Configuration Discussion Summary**

---

**Core Question:** How to structure configuration files for tools (specifically RAG tool)?

---

**Key Decisions Made:**

**1. Configuration File Strategy**

**Initial Question:** Single file per tool vs. centralized `tools.yaml`?

**Resolution: Hybrid Approach**
- **Centralized `config/tools.yaml`** - Acts as registry, contains:
  - Tool enable/disable flags
  - References to detailed config files
  - Shared/common settings (ChromaDB paths, retrieval params)
  
- **Dedicated `config/rag_tool.yaml`** - Contains complex RAG-specific config:
  - Embedding models (sentence-transformers, OpenAI, etc.)
  - Chunking strategies (markdown, code, PDF)
  - File converters (PDF, DOCX, HTML)
  - Preprocessing rules
  - Collection management

**Rationale:**
- RAG tool config is 100+ lines minimum (too large for centralized file)
- Prevents `tools.yaml` bloat (would be 200+ lines with all tools)
- Easier version control and environment-specific overrides
- Maintains single source of truth via registry pattern

---

**2. Configuration Injection Architecture**

**Problem:** Who loads and passes config to tools at runtime?

**Solution: ToolRegistry Pattern**

**Flow:**
1. **friday-memory** (client) loads `config/tools.yaml` into ToolRegistry singleton
2. ToolRegistry reads `rag_tool.config_file: "./config/rag_tool.yaml"` reference
3. ToolRegistry loads detailed `rag_tool.yaml` configuration
4. **RAGTool** queries ToolRegistry for its config on instantiation
5. No direct coupling between client and tool config schemas

**Benefits:**
- Separation of concerns (client loads, tools consume)
- Single source of truth
- Testability (mock registry for unit tests)
- Flexibility (environment overrides via env vars)

---

**3. Configuration Structure**

**`config/tools.yaml` (Registry):**
```yaml
rag_tool:
  enabled: true
  config_file: "./config/rag_tool.yaml"
  chroma:
    persist_directory: "./vector/rag"
  retrieval:
    default_top_k: 5
    similarity_threshold: 0.7
```

**`config/rag_tool.yaml` (Detailed):**
```yaml
embedding:
  default_model: "sentence-transformers/all-MiniLM-L6-v2"
  models: [...]
  
chunking:
  strategies:
    markdown: {...}
    code: {...}
    pdf: {...}
    
file_converters:
  pdf: {...}
  docx: {...}
  html: {...}
  
preprocessing: {...}
collections: {...}
```

---

**4. Environment Override Support**

ToolRegistry supports:
- File-based config (default)
- Environment variable overrides (e.g., `RAG_TOOL_CHUNK_SIZE=1024`)
- Environment-specific configs (`tools.dev.yaml`, `tools.prod.yaml`)

---

**Implementation Status:**

**Confirmed:**
- Hybrid config approach (centralized registry + per-tool files)
- ToolRegistry pattern for dependency injection
- Configuration structure for RAG tool

**Pending:**
- ToolRegistry implementation
- Initial `rag_tool.yaml` parameters (chunk size, embedding model, similarity threshold)
- Initial corpus selection for ingestion

---

**Next Step:** Proceed with ToolRegistry implementation or define initial RAG tool config parameters?
  [Extraction started in background]


**RAG Ingestion Tool: Settings & Options Summary**

---

## **Core Architecture**

**Two-Pipeline Design:**
1. **Ingestion Pipeline** - Adds documents to ChromaDB collections
2. **Retrieval Pipeline** - Queries ChromaDB for context augmentation

---

## **Ingestion Tool Configuration (`rag_tool.yaml`)**

### **1. Embedding Models**

```yaml
embedding:
  default_model: "sentence-transformers/all-MiniLM-L6-v2"
  models:
    - name: "sentence-transformers/all-MiniLM-L6-v2"
      dimension: 384
      batch_size: 32
      device: "cpu"
    - name: "openai/text-embedding-ada-002"
      dimension: 1536
      api_key: "${OPENAI_API_KEY}"
      rate_limit: 3000  # requests per minute
```

**Options:**
- Multiple embedding model support (sentence-transformers, OpenAI, Cohere)
- Configurable batch size, device (CPU/GPU), rate limits
- Environment variable injection for API keys

---

### **2. Chunking Strategies**

```yaml
chunking:
  strategies:
    markdown:
      chunk_size: 512
      chunk_overlap: 50
      respect_headers: true
      min_chunk_size: 100
    
    code:
      chunk_size: 1024
      chunk_overlap: 100
      respect_functions: true
      language_specific: true
    
    pdf:
      chunk_size: 768
      chunk_overlap: 100
      preserve_formatting: false
    
    plain_text:
      chunk_size: 512
      chunk_overlap: 50
```

**Options:**
- **chunk_size** - Maximum tokens per chunk (128-2048)
- **chunk_overlap** - Overlap between chunks to preserve context (0-512)
- **respect_headers** (markdown) - Split at header boundaries
- **respect_functions** (code) - Split at function/class boundaries
- **language_specific** (code) - Python, JavaScript, etc. specific parsing
- **preserve_formatting** (PDF) - Retain tables, lists, formatting

---

### **3. File Converters**

```yaml
file_converters:
  pdf:
    engine: "pypdf"  # Options: "pypdf", "pdfplumber", "pymupdf"
    extract_images: false
    ocr_enabled: false
  
  docx:
    engine: "python-docx"
    preserve_tables: true
  
  html:
    engine: "beautifulsoup4"
    remove_scripts: true
    remove_styles: true
  
  code:
    supported_languages: ["python", "javascript", "yaml", "json", "markdown"]
    extract_docstrings: true
    extract_comments: true
```

**Options:**
- **PDF:** Engine selection, image extraction, OCR for scanned documents
- **DOCX:** Table preservation, style extraction
- **HTML:** Script/style removal, clean text extraction
- **Code:** Language-specific parsing, docstring/comment extraction

---

### **4. Preprocessing**

```yaml
preprocessing:
  deduplicate: true
  min_content_length: 50
  remove_urls: false
  normalize_whitespace: true
  remove_code_comments: false  # For code files
  extract_metadata: true
```

**Options:**
- **deduplicate** - Remove duplicate chunks
- **min_content_length** - Skip chunks below threshold
- **remove_urls** - Strip URLs from text
- **normalize_whitespace** - Collapse multiple spaces/newlines
- **remove_code_comments** - Strip comments from code (optional)
- **extract_metadata** - Parse frontmatter, docstrings, file headers

---

### **5. Recursive Directory Ingestion**

```yaml
ingestion:
  directories:
    friday_codebase:
      path: "/path/to/friday-project"
      patterns:
        include: ["*.py", "*.md"]
        exclude: ["__pycache__", "*.pyc", "venv/", ".git/", "node_modules/"]
      recursive: true
      collection_name: "friday_codebase"
      chunking_strategy: "code"
      max_files: null  # No limit
      max_file_size_mb: 10  # Skip files larger than 10MB
    
    friday_docs:
      path: "/path/to/friday-project/docs"
      patterns:
        include: ["*.md", "*.rst"]
        exclude: []
      recursive: true
      collection_name: "friday_docs"
      chunking_strategy: "markdown"
```

**Options:**
- **path** - Root directory to scan
- **patterns.include** - Glob patterns for files to ingest (e.g., `*.py`, `**/*.md`)
- **patterns.exclude** - Patterns to skip (e.g., `__pycache__`, `.git/`)
- **recursive** - Traverse subdirectories (true/false)
- **collection_name** - Target ChromaDB collection
- **chunking_strategy** - Which chunking strategy to apply
- **max_files** - Limit number of files ingested (null = no limit)
- **max_file_size_mb** - Skip files exceeding size threshold

---

### **6. ChromaDB Collection Management**

```yaml
collections:
  auto_create: true
  naming_convention: "friday_rag_{source}_{timestamp}"
  metadata_schema:
    - source_file
    - file_type
    - directory
    - ingestion_timestamp
    - chunk_index
    - line_numbers  # For code chunks
    - git_commit  # Optional
  
  persistence:
    persist_directory: "./vector/rag"
    backup_enabled: true
    backup_interval: 86400  # seconds (daily)
```

**Options:**
- **auto_create** - Create collection if doesn't exist
- **naming_convention** - Template for collection names
- **metadata_schema** - Fields to store with each chunk
- **persist_directory** - ChromaDB storage location
- **backup_enabled** - Automatic backups
- **backup_interval** - Backup frequency (seconds)

---

### **7. Incremental Ingestion**

```yaml
incremental:
  enabled: true
  check_interval: 3600  # Re-scan every hour
  auto_update: false  # Require explicit trigger
  track_modifications: true
  hash_algorithm: "sha256"  # For detecting file changes
```

**Options:**
- **enabled** - Enable incremental ingestion
- **check_interval** - How often to check for changes (seconds)
- **auto_update** - Automatically re-ingest modified files
- **track_modifications** - Monitor file modification timestamps
- **hash_algorithm** - Algorithm for detecting content changes

---

## **Ingestion Tool Functions**

### **Function 1: Single File Ingestion**

```python
def ingest_document(
    file_path: str,
    collection_name: Optional[str] = None,
    chunking_strategy: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> IngestionResult:
    """Ingest single document into ChromaDB.
    
    Args:
        file_path: Path to document
        collection_name: Target collection (auto-creates if None)
        chunking_strategy: Override default strategy
        metadata: Additional metadata (author, tags, etc.)
    
    Returns:
        IngestionResult(
            document_id: str,
            chunk_count: int,
            collection: str,
            errors: List[str]
        )
    """
```

**Trigger Commands:**
- `"Friday, ingest this document: /path/to/file.md"`
- `"Friday, remember this file: /path/to/code.py"`
- `"Friday, add /path/to/doc.pdf to the knowledge base"`

---

### **Function 2: Recursive Directory Ingestion**

```python
def ingest_directory(
    directory_path: str,
    pattern: str = "*",
    recursive: bool = True,
    collection_name: Optional[str] = None,
    exclude_patterns: Optional[List[str]] = None
) -> IngestionResult:
    """Recursively ingest files matching pattern.
    
    Args:
        directory_path: Root directory
        pattern: Glob pattern (e.g., "*.py", "**/*.md")
        recursive: Traverse subdirectories
        collection_name: Target collection
        exclude_patterns: Patterns to skip
    
    Returns:
        IngestionResult(
            file_count: int,
            chunk_count: int,
            collection: str,
            errors: List[str]
        )
    """
```

**Trigger Commands:**
- `"Friday, ingest all Python files in /path/to/project"`
- `"Friday, index the docs directory"`
- `"Friday, load all markdown files from /path/to/docs"`

---

### **Function 3: Incremental Update**

```python
def ingest_directory_incremental(
    directory_path: str,
    collection_name: str,
    last_ingestion_timestamp: Optional[datetime] = None
) -> IngestionResult:
    """Ingest only new/modified files.
    
    Args:
        directory_path: Root directory
        collection_name: Existing collection
        last_ingestion_timestamp: Only ingest files modified after this
    
    Returns:
        IngestionResult(
            new_files: int,
            updated_files: int,
            unchanged_files: int,
            errors: List[str]
        )
    """
```

**Trigger Commands:**
- `"Friday, update the codebase index"`
- `"Friday, refresh the knowledge base"`
- `"Friday, check for new documents in /path/to/docs"`

---

## **Metadata Preserved Per Chunk**

```python
chunk_metadata = {
    "source_file": "/path/to/file.py",
    "file_type": ".py",
    "directory": "/path/to",
    "ingestion_timestamp": "2026-01-20T18:45:00Z",
    "chunk_index": 3,  # Position within file
    "line_numbers": "45-67",  # For code chunks
    "git_commit": "a1b2c3d4",  # Optional
    "author": "Chuck Russell",  # Optional
    "tags": ["phase_0_1", "display_logic"]  # Optional
}
```

---

## **Default Exclude Patterns**

```yaml
default_excludes:
  - "__pycache__"
  - "*.pyc"
  - "*.pyo"
  - ".git/"
  - ".venv/"
  - "venv/"
  - "node_modules/"
  - ".DS_Store"
  - "*.log"
  - ".pytest_cache/"
  - "*.egg-info/"
```

---

## **Configuration Injection (ToolRegistry)**

**Centralized `config/tools.yaml`:**
```yaml
rag_tool:
  enabled: true
  config_file: "./config/rag_tool.yaml"
  chroma:
    persist_directory: "./vector/rag"
```

**Detailed `config/rag_tool.yaml`:**
- Contains all settings above (embedding, chunking, converters, preprocessing, etc.)

**Loading Flow:**
1. friday-memory loads `tools.yaml` into ToolRegistry
2. ToolRegistry reads `rag_tool.config_file` reference
3. ToolRegistry loads `rag_tool.yaml`
4. RAGTool queries ToolRegistry for config on instantiation

---

## **Environment Overrides**

```bash
# Override chunk size
export RAG_TOOL_CHUNK_SIZE=1024

# Override ChromaDB path
export RAG_TOOL_CHROMA_PERSIST_DIRECTORY=/mnt/vector/rag

# Override embedding model
export RAG_TOOL_EMBEDDING_DEFAULT_MODEL="openai/text-embedding-ada-002"
```

---

## **Summary of Key Settings**

| Setting | Default | Options | Purpose |
|---------|---------|---------|---------|
| **chunk_size** | 512 | 128-2048 | Maximum tokens per chunk |
| **chunk_overlap** | 50 | 0-512 | Context preservation between chunks |
| **embedding_model** | sentence-transformers/all-MiniLM-L6-v2 | sentence-transformers, OpenAI, Cohere | Vector representation |
| **recursive** | true | true/false | Traverse subdirectories |
| **auto_create** | true | true/false | Create collections automatically |
| **deduplicate** | true | true/false | Remove duplicate chunks |
| **incremental** | true | true/false | Only ingest new/modified files |
| **max_file_size_mb** | 10 | 1-100 | Skip large files |

---

**Actionable Directive:**

Confirm initial settings for `rag_tool.yaml`. Specify first directory to ingest (`/path/to/friday-project`?). Define include patterns (`*.py`, `*.md`?) and exclude patterns (default list above?). Confirm chunk size (512 tokens?) and embedding model (sentence-transformers?).

Ready to proceed with implementation?
  [Extraction started in background]
Chuck: 
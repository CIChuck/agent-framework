# **Friday Lab Environment: The "MRI Suite"**

Status: Operational alongside Batch 0 & Batch 1\.  
Goal: To move beyond "unit testing" (does it crash?) to "cognitive testing" (is it smart?). This environment provides the Observability, Evaluation, and Optimization tools needed to inspect the Friday Framework's memory and context subsystems.

## **1\. The Lab Stack**

We use a multi-stage pipeline to inspect, improve, and interact with the system.

| Stage | Tool | Role | Integration Point |
| :---- | :---- | :---- | :---- |
| **1\. See** | **Arize Phoenix** | **Observability (The MRI)** | Integrated via TelemetryInterface (Batch 0). visualizes latency waterfalls, retrieved vector chunks, and exact trace paths. |
| **2\. Grade** | **Ragas** | **Evaluation (The Ruler)** | Used in tests/lab/. Grades "Context Precision" (Signal-to-Noise) and "Context Recall" (Missing Info) using a Judge LLM. |
| **3\. Fix** | **DSPy** | **Optimization (The Coach)** | Used in packages/friday-optimization/. Compiles better prompts for "Summarization" and "Query Generation" based on Ragas scores. |
| **4\. Visualize** | **PyVis** | **Graph Inspector** | Exports ElementX in-memory graphs to interactive HTML to verify node merging and lineage. |
| **5\. Interact** | **Streamlit** | **Lab Dashboard** | A simple web UI to manually trigger recall, consolidate, and view raw ContextPayload JSON. |

## **2\. Lab Setup & Workflow**

The Lab is not just a folder; it is a **workflow** that runs parallel to development.

### **2.1. Directory Structure**

friday-monorepo/  
├── packages/  
│   └── friday-optimization/  \# The DSPy Playground  
│       ├── compilers/        \# Scripts to optimize prompts  
│       └── signatures/       \# DSPy Modules (e.g., Summarizer)  
└── tests/  
    └── lab/                  \# The Experiments  
        ├── conftest.py       \# Fixtures (Phoenix collectors)  
        ├── datasets/         \# Golden Q\&A pairs for Ragas  
        └── experiments/      \# The 10 Scripts below

### **2.2. The Feedback Loop**

1. **Run Experiment:** Execute a script in tests/lab/.  
2. **Inspect Trace:** Open local Phoenix dashboard (http://localhost:6006).  
3. **Check Score:** Ragas returns a score (0.0 \- 1.0).  
4. **Visualize:** Open generated graph\_dump.html in browser.

## **3\. The 10 Foundation Experiments**

These experiments are designed to validate **Batch 0 (Scaffolding)** and **Batch 1 (Data Layer)** immediately, without needing the full Agent (Batch 3).

### **Phase A: Scaffolding & Plumbing (Batch 0\)**

#### **Experiment 1: The "Live Wire" Test (Telemetry)**

* **Goal:** Verify Arize Phoenix is receiving traces from the Core.  
* **Action:** Inject PhoenixTelemetryRecorder into MemoryController. Call recall() (stub).  
* **Success Criteria:** Phoenix Dashboard shows a trace named memory\_recall with duration \> 0ms and correct metadata tags.

#### **Experiment 2: Configuration Safety Check**

* **Goal:** Prove "Configuration Injection" works and prevents .env leaks.  
* **Action:** Initialize ElementXGraphStore *without* setting any environment variables. Pass explicit config dict.  
* **Success Criteria:** Component initializes successfully. Trying to initialize *without* params raises TypeError (proving it doesn't fall back to hidden env vars).

### **Phase B: Data Layer Integrity (Batch 1\)**

#### **Experiment 3: The "Amnesia" Test (Graph Persistence)**

* **Goal:** Verify ElementXGraphStore actually saves to disk.  
* **Action:**  
  1. Initialize Store A. Add Node "Project X".  
  2. **Kill Store A** (Delete object from memory).  
  3. Initialize Store B pointing to same path.  
  4. Get Node "Project X".  
* **Success Criteria:** "Project X" is retrieved with all properties intact.

#### **Experiment 4: Lineage Enforcement (Provenance)**

* **Goal:** Ensure the Schema prevents "Magic Context."  
* **Action:** Try to add a GraphNode with provenance=None or partial metadata.  
* **Success Criteria:** Pydantic raises ValidationError.

#### **Experiment 5: The "Doppelgänger" Test (Entity Merging)**

* **Goal:** Visual verification of merge\_nodes logic.  
* **Action:**  
  1. Create Node A ("Bob") and Node B ("Robert").  
  2. Add edge B \-\> \[Authored\] \-\> Doc1.  
  3. Call merge\_nodes(primary="Bob", secondary="Robert").  
  4. Export to PyVis.  
* **Success Criteria:** HTML Graph shows only "Bob". The edge "Bob \-\> Authored \-\> Doc1" exists. "Robert" is gone.

#### **Experiment 6: Time Travel (Pruning)**

* **Goal:** Verify VectorStoreAdapter.delete\_where.  
* **Action:**  
  1. Ingest 10 chunks with metadata timestamp: 2023-01-01.  
  2. Ingest 10 chunks with metadata timestamp: 2024-01-01.  
  3. Call delete\_where({'timestamp': {'$lt': '2023-12-31'}}).  
* **Success Criteria:** Querying the store returns only 2024 docs.

### **Phase C: Quality Baselines (Pre-Agent)**

#### **Experiment 7: Ingestion "Gunk" Test**

* **Goal:** Evaluate DocumentIngestionPipeline cleaning.  
* **Action:** Feed in a messy PDF/HTML with headers/footers/ads.  
* **Measure:** Manually inspect chunks in Phoenix.  
* **Success Criteria:** No "Page 1 of 50" footers or "Click Here" buttons in the text chunks.

#### **Experiment 8: The "Needle in a Haystack" (Vector Recall)**

* **Goal:** Baseline Ragas Score for ChromaVectorStore.  
* **Action:**  
  1. Ingest 50 technical documents.  
  2. Run 20 queries with known answers (Golden Dataset).  
  3. Use Ragas to calculate ContextRecall.  
* **Success Criteria:** ContextRecall \> 0.8. If lower, we know our chunking strategy (Batch 1\) needs tuning *before* we build the Agent.

#### **Experiment 9: Hybrid Search Latency**

* **Goal:** Performance profiling.  
* **Action:** Load Vector Store with 10k mock vectors. Run query(hybrid=True).  
* **Success Criteria:** Latency \< 200ms in Phoenix. If slower, we need to optimize the BM25 implementation in Batch 1\.

#### **Experiment 10: "Lost in Translation" (Embedding Quality)**

* **Goal:** Verify the embedding\_model wrapper works.  
* **Action:** Embed "Python function" and "Java method". Measure cosine similarity.  
* **Success Criteria:** Similarity should be high (conceptual match). Embed "Python function" and "Apple Pie". Similarity should be low.
# **Friday Framework \- Architecture Review and Roadmap**

This document serves as a checkpoint to validate the architectural integrity of the Friday Framework. It maps our current specifications against the master implementation plan and identifies the critical interrelationships established so far.

## **1\. Implementation Roadmap Status**

We are following a dependency-driven build order. Items marked **\[SPECIFIED\]** have complete architectural definitions ready for coding.

| Step | Component | Status | Dependency Note |
| :---- | :---- | :---- | :---- |
| **1** | **IO Adapter Protocols (ABCs)** | **\[SPECIFIED \- Batch 1\]** | *Foundation for swappability.* |
| **2** | **GraphDB Wrapper (ElementX)** | **\[SPECIFIED \- Batch 1\]** | *Requires Step 1\.* |
| **3** | **Vector/Data Store Adapters** | **\[SPECIFIED \- Batch 1\]** | *Requires Step 1\.* |
| **4** | **Document Ingestion Pipeline** | **\[SPECIFIED \- Batch 1\]** | *New component added for robust file handling.* |
| **5** | **Memory Controller Logic** | **\[SPECIFIED \- Batch 2\]** | *The "Brain". Requires Steps 2 & 3\.* |
| **6** | **Context Engineering Framework** | **\[SPECIFIED \- Batch 2\]** | *The "Editor". Requires Step 5\.* |
| 7 | **LLM Framework Config (LiteLLM)** | \[PENDING \- Batch 3\] | *The "Voice".* |
| 8 | **Telemetry Adapter** | \[PENDING \- Batch 3\] | *The "Nervous System". Must wrap previous layers.* |
| 9 | **Agent Base Class (Orchestrator)** | \[PENDING \- Batch 3\] | *The "Body". ties Brain, Voice, and IO together.* |
| 10 | **Tooling Interface (Pydantic)** | \[PENDING \- Batch 4\] | *The "Hands".* |
| 11 | **Guardrails Framework** | \[PENDING \- Batch 4\] | *Safety layer.* |
| 12 | **Event Bus** | \[PENDING \- Batch 5\] | *Asynchronous operations.* |
| 13 | **Copilot / CLI Implementation** | \[PENDING \- Batch 5\] | *Final Application logic.* |

## **2\. Specification Summary & Interrelationships**

We have effectively defined the **"Mind"** of the application. The diagram below illustrates the data flow established by Batch 1 and Batch 2\.

### **The "Memory Loop" (Established)**

graph TD  
    UserInput\[User Input\] \--\> ContextEngine  
      
    subgraph "Batch 2: Intelligence Layer"  
        ContextEngine\[Context Engine\] \-- "Asks for context" \--\> MemoryController  
        MemoryController \-- "Routes data" \--\> VectorStoreAdapter  
        MemoryController \-- "Routes data" \--\> GraphStoreAdapter  
        MemoryController \-- "Prunes/Updates" \--\> EpisodicMemory  
    end

    subgraph "Batch 1: Data Layer"  
        VectorStoreAdapter \-- "Semantic Search" \--\> ChromaDB  
        GraphStoreAdapter \-- "Traversal" \--\> ElementX  
        DocPipeline\[Ingestion Pipeline\] \-- "Chunks & Embeds" \--\> VectorStoreAdapter  
    end

    MemoryController \-- "Reinforces (Hit Counts)" \--\> GraphStoreAdapter

### **Batch 1: The Data Foundation**

* **Goal:** Swappability & Persistence.  
* **Key Achievement:** We separated *file parsing* (DocumentIngestionPipeline) from *storage* (VectorStoreAdapter).  
* **Key Achievement:** We enforced **Strong Typing** in the GraphDB (GraphNode/GraphEdge Pydantic models) to prevent unstructured chaos.

### **Batch 2: The Intelligence Core**

* **Goal:** Routing & Relevance.  
* **Key Achievement:** The **"Auto-Memorize"** feature. The Agent doesn't manually save files; the MemoryController decides if an input is a *Fact* (Graph) or a *Document* (Vector).  
* **Key Achievement:** **Hebbian Learning.** We added the hit\_count logic to the Graph Schema (retroactively) and the Memory Controller to ensure frequently accessed knowledge becomes "stronger."

## **3\. Gap Analysis: What is Missing?**

To complete the "Core Components" before expanding to features, we must address the following in **Batch 3**:

### **A. The Execution Layer (The "Body")**

Currently, we have a Brain (MemoryController) and Storage, but nothing to **execute actions** or **speak**.

* **Agent Base Class:** We need the standard loop: Observe \-\> Think (Context) \-\> Act (Tools) \-\> Reflect (Memory).  
* **LLM Configuration:** We need to define how litellm is configured (Model fallbacks, retries, API key management).

### **B. The Nervous System (Observability)**

* **Telemetry:** You correctly identified this earlier. We need the TelemetryAdapter specifications *now* so we can wrap the MemoryController and GraphDB methods we just defined. If we wait, we will have to refactor strictly defined code.

### **C. The Tools Interface**

* The ContextPayload (Batch 2\) assumes it can retrieve "Tools" to show the LLM, but we haven't defined the **Tool Registry** or the **Pydantic Schema** for tools yet.

## **4\. Recommendation for Next Steps**

Immediate Priority: Batch 3 Specification  
Focus on connecting the "Brain" (Batch 2\) to the outside world.

1. **Telemetry Adapter:** Define the tracing interfaces (OpenTelemetry) to wrap Batch 1 & 2 components.  
2. **LLM Framework:** Define the ModelWrapper that handles the actual inference calls via litellm.  
3. **Agent Core:** Define the AgentBase class that orchestrates the MemoryController and LLM.

Secondary Priority: Batch 4 Specification  
Focus on Safety and Capabilities.

1. **Tool Registry:** How we register Python functions as tools.  
2. **Guardrails:** Input/Output sanitation.
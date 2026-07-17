# **Friday Framework \- Component Specifications \- Batch 1**

**Focus:** IO Interfaces & Graph/Persistence Layer

This document outlines the technical specifications for the foundational data layers of the Friday Framework. These components are the "Muscle" of the system, handling the raw storage and retrieval of information.

**Architectural Alignment:**

* **Batch 0:** Adheres to Configuration Injection and Telemetry standards.  
* **Batch 2:** Provides the atomic CRUD operations needed by the MemoryController.

## **1\. IO Adapter Layer (The "Swappability" Protocols)**

**Classification:** Red (Framework)

**Goal:** Define strict Python Protocols or Abstract Base Classes (ABCs) that all database implementations must adhere to. This allows us to swap Chroma for FAISS or NetworkX for Neo4j without changing a single line of Agent code.

### **1.1. EpisodicStoreAdapter (Protocol)**

Defines how the application interacts with short-term conversation history. Critical for the "Context Engineering" extraction cycle.

```
class EpisodicStoreAdapter(ABC):
    @abstractmethod
    async def add_turn(self, session_id: str, turn: 'InteractionTurn') -> bool:
        """Logs a single user/assistant interaction."""
        pass

    @abstractmethod
    async def get_turns(self, session_id: str, limit: int = 10, offset: int = 0) -> List['InteractionTurn']:
        """Retrieves chronological history for context injection."""
        pass

    @abstractmethod
    async def get_unconsolidated_turns(self, session_id: str) -> List['InteractionTurn']:
        """
        Retrieves turns that have NOT yet been processed by the Memory Consolidator.
        Used by the 'Extraction' cycle.
        """
        pass

    @abstractmethod
    async def mark_consolidated(self, turn_ids: List[str]) -> bool:
        """Marks specific turns as 'processed' so they aren't re-extracted."""
        pass

    # --- NEW: Time Travel Support (Google ADK Parity) ---
    @abstractmethod
    async def rewind_history(self, session_id: str, target_turn_id: str) -> bool:
        """
        Hard Reset: Deletes all interaction turns *after* the target_turn_id.
        Used to recover from 'death spirals' or logic errors.
        """
        pass
```
### **1.2. VectorStoreAdapter (Protocol)**

Defines how the application interacts with semantic search.

* **Interface Definition:**  
  class VectorStoreAdapter(ABC):  
      @abstractmethod  
      async def add\_documents(self, texts: List\[str\], metadatas: List\[Dict\], ids: List\[str\]) \-\> bool:  
          """Embeds and stores raw text using internal model."""  
          pass

      @abstractmethod  
      async def query(self, query\_text: str, n\_results: int \= 5, where: Dict \= None, rerank: bool \= False, hybrid: bool \= False) \-\> List\[Dict\]:  
          """Standard semantic retrieval."""  
          pass

      @abstractmethod  
      async def delete(self, ids: List\[str\]) \-\> bool:  
          """Removes documents by ID."""  
          pass

      @abstractmethod  
      async def delete\_where(self, where: Dict) \-\> int:  
          """  
          Removes documents matching a metadata filter.  
          Essential for time-based pruning (e.g., {'timestamp': {'$lt': ...}}).  
          """  
          pass

### **1.3. GraphStoreAdapter (Protocol)**

Defines how the application interacts with the relationship graph.

* **Interface Definition:**  
  class GraphStoreAdapter(ABC):  
      \# \--- CRUD \---  
      @abstractmethod  
      async def add\_node(self, node: 'GraphNode') \-\> bool:  
          pass

      @abstractmethod  
      async def add\_edge(self, edge: 'GraphEdge') \-\> bool:  
          pass

      @abstractmethod  
      async def remove\_node(self, node\_id: str) \-\> bool:  
          pass

      \# \--- Traversal \---  
      @abstractmethod  
      async def get\_neighbors(self, node\_id: str, depth: int \= 1\) \-\> List\[Dict\]:  
          pass

      @abstractmethod  
      async def find\_path(self, start\_id: str, end\_id: str, max\_depth: int \= 5\) \-\> List\[str\]:  
          pass

      \# \--- Maintenance & Intelligence (Context Eng Support) \---  
      @abstractmethod  
      async def merge\_nodes(self, primary\_id: str, secondary\_id: str) \-\> bool:  
          """  
          Moves all edges from secondary node to primary node, then deletes secondary.  
          Crucial for 'Consolidation' cycle (Entity Resolution).  
          """  
          pass

      @abstractmethod  
      async def fuzzy\_search(self, query: str, threshold: float \= 0.8) \-\> List\['GraphNode'\]:  
          """  
          Finds nodes with similar names/labels.   
          Used to prevent duplicate entity creation (e.g., 'Bob' vs 'Robert').  
          """  
          pass

      @abstractmethod  
      async def rank\_nodes(self, algorithm: str \= "pagerank") \-\> List\[Dict\]:  
          pass

## **2\. GraphDB Implementation (Schema with Provenance)**

Classification: Orange (Component)  
Target Tech: ElementX / NetworkX \+ Pydantic

### **2.1. Schema Enforcement**

We strictly enforce **Provenance** to track where memories come from.

class ProvenanceMetadata(BaseModel):  
    source\_id: str        \# UUID of the Turn or Document  
    source\_type: str      \# 'interaction', 'document', 'inference'  
    confidence: float     \# 0.0 to 1.0  
    created\_at: datetime  
    author\_id: Optional\[str\] \= None \# 'user\_123' or 'agent\_friday'

class GraphNode(BaseModel):  
    id: str  
    type: str \# 'Entity', 'Concept', 'Event'  
    properties: Dict\[str, Any\]  
    provenance: ProvenanceMetadata \# Required for Lineage  
    hit\_count: int \= 0  
    last\_accessed: datetime

class GraphEdge(BaseModel):  
    source\_id: str  
    target\_id: str  
    relation: str  
    properties: Dict\[str, Any\]  
    provenance: ProvenanceMetadata \# Required for Lineage  
    weight: float \= 1.0

### **2.2. Class: ElementXGraphStore**

* **Inherits:** GraphStoreAdapter  
* Configuration (Injection Only):  
  This class MUST NOT read environment variables or FridayBaseSettings directly.  
  It MUST accept an optional telemetry recorder for white-box testing.  
  class ElementXGraphStore(GraphStoreAdapter):  
      def \_\_init\_\_(self,   
                   storage\_path: str,   
                   schema\_config: Dict\[str, Any\] \= None,  
                   telemetry: Optional\['TelemetryInterface'\] \= None):  
          """  
          Args:  
              storage\_path: Absolute path to the .gpickle or .json file.  
              schema\_config: Optional dict defining allowed Node Types/Edge Relations.  
              telemetry: Telemetry hook for recording internal events (latency, cache hits).  
          """  
          self.storage\_path \= storage\_path  
          self.telemetry \= telemetry  
          \# ... Init logic ...

* **Implementation Note (Merge Logic):**  
  * merge\_nodes(A, B):  
    1. Identify all edges where B is source/target.  
    2. Create copies of those edges pointing to/from A.  
    3. Copy unique properties from B to A (conflict resolution: A wins).  
    4. Delete B.  
    5. *Telemetry:* Emit graph\_node\_merged event.

## **3\. Vector Store Implementation**

Classification: Orange (Component)  
Target Tech: chromadb

### **3.1. Class: ChromaVectorStore**

* **Inherits:** VectorStoreAdapter  
* **Configuration (Injection Only):**  
  class ChromaVectorStore(VectorStoreAdapter):  
      def \_\_init\_\_(self,   
                   collection\_name: str,   
                   persist\_directory: str,   
                   embedding\_model: Any,  
                   telemetry: Optional\['TelemetryInterface'\] \= None):  
          """  
          Args:  
              collection\_name: The namespace for this memory (e.g., 'friday\_long\_term').  
              persist\_directory: Local path for Chroma storage.  
              embedding\_model: An initialized wrapper (e.g., SentenceTransformer) providing \`.encode()\`.  
              telemetry: Telemetry hook.  
          """  
          self.client \= chromadb.PersistentClient(path=persist\_directory)  
          self.collection \= self.client.get\_or\_create\_collection(name=collection\_name)  
          self.embedding\_model \= embedding\_model  
          self.telemetry \= telemetry

## **4\. Capability Layer: Document Ingestion**

**Classification:** Blue (Capability)

### **4.1. Class: DocumentIngestionPipeline**

* **Responsibilities:** File Parsing \-\> Text Chunking \-\> Metadata Extraction.  
* **Output:** Now includes provenance metadata in the standard format expected by the adapters.  
* Configuration: \`\`\`python  
  class DocumentIngestionPipeline:  
  def init(self, chunk\_size: int \= 500, overlap: int \= 50):  
  self.chunk\_size \= chunk\_size  
  self.overlap \= overlap

## **5\. Acceptance Criteria for Batch 1**

1. **Configuration Isolation:**  
   * Initialize ElementXGraphStore with a temp path in a unit test. Ensure it does *not* look for a .env file.  
   * Initialize ChromaVectorStore with a mock embedding model.  
2. **Telemetry Verification:**  
   * Inject a DebugTelemetryRecorder into ElementXGraphStore.  
   * Perform add\_node.  
   * Verify recorder.events contains a graph\_node\_added event.  
3. **Strict Provenance:**  
   * Attempting to create a GraphNode without a provenance block must raise a Pydantic ValidationError.  
4. **Episodic Flow:**  
   * Test add\_turn \-\> get\_unconsolidated\_turns (returns 1\) \-\> mark\_consolidated \-\> get\_unconsolidated\_turns (returns 0).  
5. **Entity Resolution:**  
   * Create Node A ("Robert") and Node B ("Bob"). Add edge B-\>C.  
   * Call merge\_nodes(A, B).  
   * Verify B is gone. Verify edge A-\>C exists.
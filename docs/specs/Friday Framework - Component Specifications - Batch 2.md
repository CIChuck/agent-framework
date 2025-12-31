# **Friday Framework \- Component Specifications \- Batch 2**

**Focus:** Memory Controller (The Unified Data Facade)

Architectural Role:  
The MemoryController sits between the Data Layer (Batch 1 Adapters) and the Context Strategies (Batch 2a). It is the "Body" that executes the "Brain's" commands. It provides a unified API to read/write across Vector, Graph, and Episodic stores simultaneously.

## **1\. Data Structures (The Contract)**

### **1.1. ContextPayload (DTO)**

The standardized container for retrieved information. It aligns strictly with Batch 2a's "Provenance" requirements.

@dataclass  
class ContextPayload:  
    \# \--- Episodic Memory \---  
    \# The immediate narrative thread.  
    history: List\['InteractionTurn'\] 

    \# \--- Semantic Memory (Vector) \---  
    \# Specific passages (chunks) relevant to the query.  
    \# Must include 'provenance' (source\_id, confidence).  
    passages: List\[Dict\[str, Any\]\] 

    \# \--- Associative Memory (Graph) \---  
    \# Fully hydrated nodes representing entities/concepts.  
    entities: List\['GraphNode'\]

    \# Relationships explaining \*why\* entities were retrieved.  
    facts: List\['GraphEdge'\]  
```
# --- NEW: Transparency Layer (Anthropic Parity) ---
    # A list of facts/insights the System auto-archived since the last turn.
    # Gives the Agent confidence that "Implicit Extraction" is working.
    # e.g., ["Archived fact: User prefers Python", "Consolidated 3 turns"]
    recent_memories: List[str]
```
      
    \# \--- Meta-Cognition \---  
    \# Debug info: {'vector\_latency': 0.1, 'graph\_nodes\_touched': 15}  
    debug\_info: Dict\[str, Any\]

## **2\. Memory Controller (The Facade)**

Classification: Blue (Abstraction)  
Dependencies: VectorStoreAdapter, GraphStoreAdapter, EpisodicStoreAdapter

### **2.1. Initialization**

class MemoryController:  
    def \_\_init\_\_(self,   
                 vector\_store: VectorStoreAdapter,   
                 graph\_store: GraphStoreAdapter,   
                 episodic\_store: EpisodicStoreAdapter):  
        self.vector \= vector\_store  
        self.graph \= graph\_store  
        self.episodic \= episodic\_store

### **2.2. Core API: Retrieval (The "Recall" Loop)**

Used by ContextAssembler (Batch 2a) to build the prompt.

    async def recall(self,   
                     query: str,   
                     token\_limit: int \= 2000,   
                     include\_history: bool \= True) \-\> 'ContextPayload':  
        """  
        Orchestrates parallel retrieval from all memory stores.  
          
        1\. \*\*Episodic:\*\* Fetches recent turns (if include\_history=True).  
        2\. \*\*Vector:\*\* Queries chunks using 'Hybrid Search' (Keyword \+ Semantic).  
        3\. \*\*Graph:\*\* \- Extracts entities from query (NER).  
            \- Traversals: \`get\_neighbors(depth=1)\` for immediate context.  
            \- Reinforcement: Triggers \`touch\_nodes\` (Hebbian learning).  
        4\. \*\*Fusion:\*\* Deduplicates entities found in both Vector/Graph.  
        """  
        pass

### **2.3. Core API: Storage (The "Memorize" Loop)**

Used by MemoryExtractor (Batch 2a) to save new insights.

    async def store\_fact(self, node: 'GraphNode', edge: 'GraphEdge' \= None) \-\> bool:  
        """  
        Writes a specific entity/fact to the Graph.  
        \*Validates\* that \`node.provenance\` is populated.  
        """  
        pass

    async def store\_insight(self, text: str, metadata: 'ProvenanceMetadata') \-\> bool:  
        """  
        Writes a semantic block (e.g., summary) to the Vector store.  
        """  
        pass

### **2.4. Core API: Maintenance (The "Consolidate" Loop)**

Used by MemoryConsolidator (Batch 2a) to clean up memory.

    async def fetch\_unconsolidated\_events(self, session\_id: str) \-\> List\['InteractionTurn'\]:  
        """Proxies EpisodicStoreAdapter.get\_unconsolidated\_turns."""  
        pass

    async def mark\_events\_consolidated(self, event\_ids: List\[str\]) \-\> bool:  
        """Proxies EpisodicStoreAdapter.mark\_consolidated."""  
        pass

    async def merge\_identities(self, primary\_id: str, secondary\_id: str) \-\> bool:  
        """  
        Proxies GraphStoreAdapter.merge\_nodes.  
        Used when the Agent realizes 'Bob' and 'Robert' are the same person.  
        """  
        pass

## **3\. Acceptance Criteria for Batch 2**

1. **Test: Provenance Enforcement**  
   * **Action:** Call store\_insight("Test", metadata=None).  
   * **Result:** Must raise ValidationError (or similar) because Batch 1/2a rules demand lineage.  
2. **Test: The Consolidation Bridge**  
   * **Setup:** Insert 5 "raw" turns into EpisodicStore.  
   * **Action:** Call MemoryController.fetch\_unconsolidated\_events().  
   * **Result:** Returns 5 turns.  
   * **Action:** Call MemoryController.mark\_events\_consolidated(\[ids\]).  
   * **Result:** Subsequent fetch returns 0 turns.  
3. **Test: Unified Recall**  
   * **Action:** recall("Project X").  
   * **Result:** ContextPayload contains:  
     * passages: Docs mentioning "Project X" (with provenance).  
     * entities: The "Project X" node (with hit\_count incremented).  
     * facts: Edges like "Project X \-\> Assigned\_To \-\> User".
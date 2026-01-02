# **Friday Framework \- Component Specifications: Batch 3**

## **0\. Introduction: The Execution Layer Manifest**

Status: Ready for Implementation  
Role: The "Body" of the Agentic Framework.  
This batch focuses on bridging the static "Brain" (Memory & Context layers defined in Batch 1 & 2\) with the dynamic "World" (User Input, LLM Inference, and Tool Execution). It transforms Friday from a passive knowledge graph into an active, thinking entity.

### **0.1. Functional Requirements & Features**

To complete Batch 3, the AI Builder must implement the following core capabilities:

1. **Observability (The "Nervous System"):**  
   * Implement OpenTelemetryProvider to wrap all operations in standard traces.  
   * **Goal:** Enable "MRI-style" inspection of the agent's thought process without logging sensitive data or cluttering stdout.  
2. **Inference Infrastructure (The "Voice"):**  
   * **Protocol Definition:** Define abstract LLMClient and EmbeddingModel interfaces in friday-core to decouple logic from providers.  
   * **Concrete Implementation:** Build friday-llm package wrapping litellm.  
   * **Reliability:** Implement tenacity-based retries for rate limits and transient errors.  
   * **Flexibility:** Support both cloud APIs (OpenAI/Anthropic) and **Local Servers** (Ollama/LM Studio) via api\_base injection.  
3. **Agent Orchestration (The "Will"):**  
   * **Identity Separation:** Implement AgentProfile to define *who* the agent is (Prompts, Goals, Capabilities) separate from the runtime code.  
   * **Polymorphic Runtime:** Implement AgentBase as an Abstract Base Class.  
   * **Behaviors:**  
     * CopilotAgent: A reactive, human-in-the-loop chat agent supporting multi-step tool use (Re-Act pattern).  
     * AutonomousAgent: A goal-directed agent capable of planning and executing task chains (placeholder for future expansion).  
4. **Capability Management (The "Hands"):**  
   * Implement ToolRegistry protocol to map string-based tool names (from Profiles) to executable Python functions.  
   * Support dynamic JSON Schema generation for LLM function calling.

### **0.2. Architectural Decisions & Directives**

* **Package Separation:** We have moved from a monolithic design to a strict package hierarchy.  
  * friday-inference \-\> Renamed to friday-llm (Pure I/O).  
  * friday-agent (New) \-\> Contains the Orchestration Logic.  
  * **Constraint:** friday-agent MUST NOT depend on friday-llm. It must depend only on friday-core interfaces. Dependency injection happens at the App layer (friday-cli).  
* **Configuration Injection:** Components must accept configuration (API keys, URLs) via \_\_init\_\_. Reading .env files inside business logic is **strictly forbidden**.  
* **Looping Architecture:** The Agent runtime is no longer a linear pipeline. It implements a while loop to handle the "Model \-\> Tool \-\> Model" cycle natively.

### **0.3. Evolution Hints for the AI Builder**

* **Streaming:** The current protocols return strings. Future iterations should introduce AsyncIterator return types for LLMClient to support real-time token streaming.  
* **Middleware:** Consider where "Safety Guardrails" fit. Ideally, they should wrap the LLMClient implementation, intercepting prompts before they leave the system.  
* **State Serialization:** As Agents become long-running, the SessionState (Batch 2a) will need robust serialization/deserialization to allow pausing and resuming agents across server restarts.

**Focus:** Execution Layer & Inference Infrastructure

Context:  
With the Data Layer (Batch 1\) and Intelligence Layer (Batch 2\) complete, we now define the components that drive execution. This batch establishes the independent Inference subsystem and the Agent orchestrator that connects it to Memory.  
**Architectural Update:**

* Inference components are packaged in friday-llm.  
* **NEW:** Agent orchestration logic is packaged in friday-agent.  
* **NEW:** AgentBase is now an Abstract Base Class (ABC) supporting polymorphic behaviors (CopilotAgent vs AutonomousAgent).  
* **NEW:** Architecture supports "Re-Act" style looping for Tool execution.

## **1\. Observability: OpenTelemetry Implementation**

Classification: Red (Framework)  
Package: packages/friday-core  
Path: packages/friday-core/src/friday\_core/telemetry.py  
**Goal:** Provide a concrete implementation of the TelemetryInterface (Batch 0\) using the OpenTelemetry standard.

### **1.1. Class: OpenTelemetryProvider**

* **Implements:** TelemetryInterface (Protocol)  
* **Dependencies:** opentelemetry-api, opentelemetry-sdk

class OpenTelemetryProvider(TelemetryInterface):
    """
    Production-grade telemetry adapter wrapping OpenTelemetry.
    Auto-instruments spans and maps internal events to OTel semantic conventions.
    """
    def \_\_init\_\_(self, service\_name: str, endpoint: str \= None):
        """
        Args:
            service\_name: e.g., 'friday-agent'
            endpoint: OTLP collector URL (optional). If None, logs to console.
        """
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.exporter.otlp.proto.grpc.trace\_exporter import OTLPSpanExporter

        provider \= TracerProvider()
        if endpoint:
            exporter \= OTLPSpanExporter(endpoint=endpoint)
        else:
            exporter \= ConsoleSpanExporter()
        provider.add\_span\_processor(BatchSpanProcessor(exporter))
        trace.set\_tracer\_provider(provider)
        self.tracer \= trace.get\_tracer(service\_name)
        self.\_active\_spans: dict[str, Any] \= {}

    def capture\_event(self, event\_name: str, data: dict[str, Any]) \-\> None:
        """Records a discrete event as a span event on the current context."""
        current\_span \= trace.get\_current\_span()
        if current\_span:
            current\_span.add\_event(event\_name, attributes=data)

    def start\_span(self, name: str, parent\_id: str | None \= None) \-\> str:
        """Starts a trace span and returns its unique ID."""
        span \= self.tracer.start\_span(name)
        span\_id \= str(uuid4())
        self.\_active\_spans[span\_id] \= span
        return span\_id

    def end\_span(self, span\_id: str, data: dict[str, Any] | None \= None) \-\> None:
        """Ends a previously started span."""
        if span\_id in self.\_active\_spans:
            span \= self.\_active\_spans.pop(span\_id)
            if data:
                for key, value in data.items():
                    span.set\_attribute(key, value)
            span.end()

**Architectural Context & Evolution Guidelines:**

* **Why this exists:** To prevent vendor lock-in. Direct logging to a specific platform (like Datadog or Arize) inside business logic makes the code brittle. This wrapper ensures the application speaks a standard dialect (OTel), allowing the infrastructure to decide where the data goes.  
* **Goals:** The primary goal is observability transparency ("The MRI"). It must capture latency, error rates, and internal decision paths (e.g., "Why did the agent choose tool X?") without cluttering the core logic with print statements.  
* **Evolution Hints for AI Builders:** Future iterations could introduce **Sampling Strategies** to reduce noise in high-volume environments (e.g., trace only 1% of successful calls but 100% of errors). You might also extend this to support **Metrics** (Counters/Histograms) alongside Traces, allowing for real-time dashboards of token usage or memory retrieval hit rates.

## **2\. Core Interfaces: Models & Tools**

Classification: Red (Framework)  
Package: packages/friday-core  
Path: packages/friday-core/src/friday\_core/interfaces/  
**Goal:** Define the protocols that friday-memory and friday-cli rely on.

### **2.1. Protocol: LLMClient (Chat)**

**Path:** src/friday\_core/interfaces/llm.py

@dataclass
class ToolCall:
    """Represents a tool call requested by the LLM."""
    id: str
    name: str
    arguments: dict[str, Any]

@dataclass
class ChatCompletionResponse:
    """Structured response from chat completion supporting tool calls."""
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0

class LLMClient(Protocol):
    async def chat\_completion(self,
                              messages: List\[Dict\],
                              tools: Optional\[List\[Dict\]\] \= None,
                              response\_model: Optional\[Type\[BaseModel\]\] \= None,
                              temperature: float \= 0.7) \-\> ChatCompletionResponse:
        """
        Abstract interface for LLM inference (Generation).
        Must support passing 'tools' (JSON Schemas) to the provider.

        Returns:
            ChatCompletionResponse with content and/or tool_calls.
            Use response.has_tool_calls to check if tools were requested.
        """
        pass

**Architectural Context & Evolution Guidelines:**

* **Why this exists:** To enforce the Dependency Inversion Principle. The friday-memory package needs to summarize text, but it should not depend on litellm or openai libraries directly. This interface allows us to inject *any* text generator—including a mock for testing or a local model—without breaking the memory system.  
* **Goals:** Provide a unified contract for text generation that abstracts away API keys, retries, and provider-specific formatting.  
* **Evolution Hints for AI Builders:** As LLMs evolve, this interface will likely need to support **Streaming** (returning an AsyncIterator instead of a string) to improve user perceived latency. Support for **Multi-modal inputs** (images, audio) should also be considered by updating the messages type hint to accept complex content blocks.

### **2.2. Protocol: EmbeddingModel (Vectors)**

**Path:** src/friday\_core/interfaces/llm.py

class EmbeddingModel(Protocol):  
    async def embed\_documents(self, texts: List\[str\]) \-\> List\[List\[float\]\]:  
        pass  
          
    async def embed\_query(self, text: str) \-\> List\[float\]:  
        pass

**Architectural Context & Evolution Guidelines:**

* **Why this exists:** Vector databases require numerical representations of text. This protocol isolates the "math conversion" logic from the storage logic.  
* **Goals:** Ensure consistent vector space operations. By separating embed\_documents and embed\_query, we support asymmetric embedding models (like E5 or BGE) that require different instructions for indexing versus searching.  
* **Evolution Hints for AI Builders:** Future implementations might add **Batching logic** directly into the interface wrapper to handle rate limits efficiently. Consider adding support for **Sparse Vectors** (SPLADE) or late-interaction models (ColBERT) which require different return types than a simple list of floats.

### **2.3. Protocol: ToolRegistry (Capabilities) (New)**

**Path:** src/friday\_core/interfaces/tools.py

class ToolRegistry(Protocol):  
    def get\_tool(self, name: str) \-\> Callable:  
        """Returns the executable function."""  
        pass  
          
    def get\_schema(self, name: str) \-\> Dict\[str, Any\]:  
        """Returns the OpenAI-compatible JSON Schema for the tool."""  
        pass  
          
    def list\_tools(self) \-\> List\[str\]:  
        """Returns all registered tool names."""  
        pass

**Architectural Context & Evolution Guidelines:**

* **Why this exists:** The AgentProfile knows the *names* of tools it wants to use, but the runtime needs the *code*. This registry acts as the bridge/catalog. It prevents the Agent from needing to import every tool definition directly.
* **Goals:** To create a pluggable system where tools can be registered dynamically. It serves as the "App Store" for the Agent.
* **Evolution Hints for AI Builders:** Evolve this into a dynamic plugin loader that can read tools from a folder or a remote repository. Consider adding **Role-Based Access Control (RBAC)** here—checking if the current Session is authorized to use the requested tool before returning it.

### **2.4. Built-in Tools (Core Memory Tools)**

**Path:** src/friday\_agent/tools/builtins.py

The framework must include a default set of tools that enable the agentic memory loop. These are registered automatically when using the default ToolRegistry implementation.

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `scratchpad_write` | Persist a key-value pair to SessionState (survives context pruning) | `key: str, value: str` |
| `scratchpad_read` | Retrieve a value from the agent's scratchpad | `key: str` |
| `recall_memory` | Search the agent's memory for relevant information | `query: str, limit: int = 5` |
| `store_fact` | Explicitly store a fact as a graph edge | `subject: str, predicate: str, object: str` |

**Example Implementation:**

```python
async def scratchpad_write(state: SessionState, key: str, value: str) -> str:
    """Write a value to the agent's scratchpad (survives context pruning)."""
    state.set_var(f"session:{key}", value)
    return f"Saved '{key}' to scratchpad"

async def recall_memory(memory_controller, query: str, limit: int = 5) -> str:
    """Search agent's memory for relevant information."""
    payload = await memory_controller.recall(query, vector_results=limit)
    results = [f"- {p.get('text', '')[:200]}..." for p in payload.passages[:limit]]
    return "\n".join(results) if results else "No relevant memories found"
```

**Rationale:** These tools enable agents to:
1. **Survive Loop Amnesia:** Persist insights via scratchpad when tool execution history is pruned
2. **Actively Query Memory:** Use recall_memory as a "Memory-as-a-Tool" pattern (Active Search from Batch 2a)
3. **Explicitly Learn:** Use store_fact for high-confidence facts the agent wants to remember permanently

## **3\. Inference Layer: Concrete Services**

Classification: Red (Framework)  
Package: packages/friday-llm  
Path: packages/friday-llm/src/friday\_llm/  
**Goal:** A dedicated package for managing Model interactions. It handles litellm wrapping, retries, and rate limiting.

### **3.1. Class: LiteLLMService (Chat)**

**Path:** src/friday\_llm/service.py

class LiteLLMService:  
    def \_\_init\_\_(self,   
                 model\_name: str,   
                 api\_key: str,   
                 telemetry: 'TelemetryInterface',  
                 api\_base: Optional\[str\] \= None,  
                 max\_retries: int \= 3):  
        self.model \= model\_name  
        self.api\_key \= api\_key  
        self.api\_base \= api\_base  
        self.telemetry \= telemetry  
        self.max\_retries \= max\_retries

    async def chat\_completion(self,   
                              messages: List\[Dict\],   
                              tools: Optional\[List\[Dict\]\] \= None,   
                              response\_model: Optional\[Type\[BaseModel\]\] \= None) \-\> Union\[str, BaseModel\]:  
        """  
        Standardized inference call using litellm.acompletion.  
        Parses litellm response to detect 'tool\_calls'.  
        """  
        pass

**Architectural Context & Evolution Guidelines:**

* **Why this exists:** LLM APIs are flaky. They timeout, rate-limit, and sometimes return malformed JSON. This service wraps that chaos in a reliable blanket (using tenacity for retries) and standardizes the output format. It serves as the "Driver" for the "Hardware" (the Model).  
* **Goals:** Reliability and Observability. Every call must be traced, every error handled gracefully.  
* **Evolution Hints for AI Builders:** Implement **Cost Tracking**—logging the token usage and estimated cost of every call to Telemetry. Add **Fallback Logic** (e.g., if GPT-4 is down, automatically degrade to GPT-3.5 or Claude without throwing an error to the user).

### **3.2. Class: LiteLLMEmbeddingService (Embeddings)**

**Path:** src/friday\_llm/embeddings.py

* **Implements:** friday\_core.interfaces.llm.EmbeddingModel

class LiteLLMEmbeddingService:  
    def \_\_init\_\_(self,   
                 model\_name: str,   
                 api\_key: str,   
                 telemetry: 'TelemetryInterface',  
                 api\_base: Optional\[str\] \= None): \# \<--- NEW: Support for Local Embeddings  
        """  
        Args:  
            model\_name: e.g., 'text-embedding-3-small' or 'ollama/nomic-embed-text'  
            api\_key: The raw key string (injected by App).  
            api\_base: URL for local embedding server (e.g., 'http://localhost:11434').  
        """  
        self.model \= model\_name  
        self.api\_key \= api\_key  
        self.api\_base \= api\_base  
        self.telemetry \= telemetry

    async def embed\_documents(self, texts: List\[str\]) \-\> List\[List\[float\]\]:  
        """  
        Wraps litellm.embedding().  
        Handles batching if the provider has limits (optional).  
        """  
        pass

    async def embed\_query(self, text: str) \-\> List\[float\]:  
        """  
        Wraps litellm.embedding() for a single string.  
        """  
        pass

**Architectural Context & Evolution Guidelines:**

* **Why this exists:** To provide a concrete implementation of the EmbeddingModel protocol using the same robust configuration (API keys, base URLs) as the chat service.  
* **Goals:** Efficient conversion of text to vectors.  
* **Evolution Hints for AI Builders:** Implement **Caching**. Embeddings are immutable for a given model version; re-embedding the same string is waste. An internal LRU cache or Redis connection here would significantly improve performance and lower costs.

## **4\. Agent Execution Layer: The Core Logic**

Classification: Blue (Abstraction)  
Package: packages/friday-agent  
Path: packages/friday-agent/src/friday\_agent/  
**Goal:** Reusable Agent orchestration logic. Segregates the **Resources** (Infrastructure) from the **Behavior** (Control Flow).

### **4.1. Class: AgentProfile (The Persona)**

**Path:** src/friday\_agent/profile.py

@dataclass  
class AgentProfile:  
    name: str  
    role: str  
    goal: str  
    system\_prompt\_template: str  
      
    \# Capabilities (The Menu)  
    \# List of strings referencing keys in the ToolRegistry  
    \# e.g., \["search\_web", "read\_file", "recall\_memory"\]  
    tools: List\[str\] \= field(default\_factory=list)  
      
    context\_strategy: str \= "standard"   
    temperature: float \= 0.7

**Architectural Context & Evolution Guidelines:**

* **Why this exists:** To separate the "Engine" (AgentBase) from the "Driver" (The Persona). We want to be able to spin up different agents (e.g., "Coding Assistant", "Researcher", "Creative Writer") using the same underlying code but different configurations.  
* **Goals:** Portability and definition. This object should be easily serializable to YAML/JSON so agents can be defined in config files.  
* **Evolution Hints for AI Builders:** Introduce **Profile Inheritance** (e.g., a "PythonDev" profile inherits tools from a generic "Dev" profile). Add **Dynamic Prompt Injection** capabilities, allowing the profile to define rules that only activate under certain conditions (e.g., "If user is angry, adopt a soothing tone").

### **4.2. Class: AgentBase (The Abstract Runtime)**

**Path:** src/friday\_agent/base.py

class AgentBase(ABC):
    def \_\_init\_\_(self,
                 profile: AgentProfile,
                 memory: 'MemoryController',
                 context\_engine: 'ContextEngineeringInterface',  # Protocol, not concrete class
                 llm: 'LLMClient',
                 tool\_registry: 'ToolRegistry',
                 telemetry: 'TelemetryInterface' \= None):  # Optional for testing
        self.profile \= profile
        self.memory \= memory
        self.context\_engine \= context\_engine
        self.llm \= llm
        self.tool\_registry \= tool\_registry
        self.telemetry \= telemetry
        self.session\_id \= str(uuid4())
        self.\_session\_state: SessionState \= None  # Lazy initialized

    @abstractmethod  
    async def run(self, input\_signal: Any) \-\> Any:  
        pass

    def \_get\_tool\_schemas(self) \-\> List\[Dict\]:  
        """Resolves profile.tools strings to JSON Schemas."""  
        return \[self.tool\_registry.get\_schema(name) for name in self.profile.tools\]

    async def \_execute\_tool\_call(self, tool\_name: str, args: Dict) \-\> str:  
        """Executes the function from the registry and returns string output."""  
        func \= self.tool\_registry.get\_tool(tool\_name)  
        return await func(\*\*args)  
          
    async def \_archive\_turn(self, role: str, content: str):
        """Helper to save interaction to Episodic Store and trigger extraction."""
        turn \= InteractionTurn(
            user\_message=content if role == "user" else None,
            assistant\_response=content if role == "assistant" else None,
        )
        await self.memory.add\_turn(self.session\_id, turn)
        # Async extraction (non-blocking background task)
        asyncio.create\_task(self.context\_engine.extract\_context(turn, async\_execution=True))

    async def \_get\_session\_state(self) \-\> SessionState:
        """Lazy-load or retrieve current session state."""
        if self.\_session\_state is None:
            self.\_session\_state \= await self.context\_engine.initialize\_session(
                self.session\_id, user\_id="default"
            )
        return self.\_session\_state

    def \_get\_scratchpad\_context(self) \-\> str:
        """
        Formats SessionState.scoped\_vars for injection into System Prompt.
        Survives context pruning by being pinned to System Block.
        """
        if self.\_session\_state is None:
            return ""
        scratchpad\_items \= []
        for key, value in self.\_session\_state.scoped\_vars.items():
            if key.startswith("session:"):
                display\_key \= key.replace("session:", "")
                scratchpad\_items.append(f"- {display\_key}: {value}")
        if not scratchpad\_items:
            return ""
        return "\\n**Agent Scratchpad:**\\n" + "\\n".join(scratchpad\_items)

**Architectural Context & Evolution Guidelines:**

* **Why this exists:** To eliminate boilerplate. Every agent, regardless of its loop style (Chat vs. Autonomous), needs to connect to Memory, resolve tools, and log telemetry. This Base Class enforces that infrastructure consistency.  
* **Goals:** Provide a stable platform for building varied agent behaviors.  
* **Evolution Hints for AI Builders:** Implement **Middleware Hooks** (pre\_run, post\_run) to allow for global interceptors—useful for safety guardrails or billing logic that applies to *all* agents. Consider adding an **Event Bus** connection here so agents can publish status updates ("I'm thinking...") to a UI.

### **4.3. Class: CopilotAgent (Concrete Implementation)**

**Path:** src/friday\_agent/copilot.py

Implements the **Reactive Tool Loop** (Re-Act Pattern).

class CopilotAgent(AgentBase):  
    """  
    Human-in-the-loop agent with Multi-Step Tool Execution capabilities.  
    Flow: Input \-\> \[Think \-\> Tool \-\> Output \-\> Think\]\* \-\> Response.  
    """  
    async def run(self, user\_input: str) \-\> str:  
        with self.telemetry.start\_span(f"copilot\_turn\_{self.profile.name}"):  
            \# 1\. Archive User Input  
            await self.\_archive\_turn("user", user\_input)  
              
            \# 2\. Context Assembly (Initial)  
            context \= await self.context\_engine.assemble\_context(...)  
            messages \= await self.context\_engine.format\_prompt(...)  
            messages.append({"role": "user", "content": user\_input})  
              
            \# 3\. Execution Loop  
            tool\_schemas \= self.\_get\_tool\_schemas()  
            final\_response \= ""  
              
            while True:  
                \# A. Inference  
                response \= await self.llm.chat\_completion(  
                    messages=messages,   
                    tools=tool\_schemas  
                )  
                  
                \# B. Check for Tool Calls  
                if hasattr(response, 'tool\_calls') and response.tool\_calls:  
                    \# Append Assistant's "Request" to history  
                    messages.append(response.message)   
                      
                    \# Execute Tools  
                    for tool\_call in response.tool\_calls:  
                        result \= await self.\_execute\_tool\_call(  
                            tool\_call.function.name,   
                            tool\_call.function.arguments  
                        )  
                        \# Append Tool Output to history  
                        messages.append({  
                            "role": "tool",   
                            "tool\_call\_id": tool\_call.id,   
                            "content": result  
                        })  
                    \# Loop back to Step A (Model sees output, decides next move)  
                    continue   
                  
                \# C. No Tools? We are done.  
                final\_response \= response.content  
                break  
              
            \# 4\. Reflect (Archive Final Response)  
            await self.\_archive\_turn("assistant", final\_response)  
              
            return final\_response

**Architectural Context & Evolution Guidelines:**

* **Why this exists:** To handle the specific dynamics of a Chatbot. It is "Reactive"—it waits for a user, does a burst of work (potentially using tools multiple times), and then stops to wait for the user again.  
* **Goals:** Seamless conversation with capability. The while True loop is critical; it allows the agent to "self-correct" or chain multiple tools (e.g., "List files" \-\> "Read file") before answering.  
* **Evolution Hints for AI Builders:** Implement **Human-in-the-loop** confirmations. Before executing a sensitive tool (like delete\_file), the agent should pause and ask the user for permission. This would require breaking the while loop into a state machine that can persist across user interrupts.

### **4.4. Class: AutonomousAgent (Concrete Implementation)**

**Path:** src/friday\_agent/autonomous.py

Implements the **Goal-Directed Loop** with Plan Decomposition.

class AutonomousAgent(AgentBase):  
    """  
    Goal-oriented agent.  
    Flow: Goal \-\> Plan \-\> \[Execute Step \-\> Verify\]\* \-\> Final Result.  
    """  
    async def run(self, goal: str) \-\> str:  
        with self.telemetry.start\_span(f"auto\_task\_{self.profile.name}"):  
            \# Similar to Copilot, but the "Input" is a task from a generated plan.  
            \# Handles tool loops within each plan step.  
            pass

**Architectural Context & Evolution Guidelines:**

* **Why this exists:** To perform long-running tasks that require planning. Unlike the Copilot, this agent isn't driven by user interrupts; it drives itself based on a goal.  
* **Goals:** Persistence and resilience. It needs to break a big problem into small steps and execute them sequentially.  
* **Evolution Hints for AI Builders:** Implement **Tree of Thoughts** or **Reflection** loops. After a step fails, the agent shouldn't just crash; it should analyze the error, replan, and try a different approach. Adding a "Critic" sub-agent loop here would significantly improve success rates.

## **5\. Test Coverage (Acceptance Criteria)**

### **5.1. Unit Tests (Isolation)**

1. **Tool Registry Resolution:**  
   * **Action:** Create AgentProfile with tools=\["test\_tool"\]. Call \_get\_tool\_schemas.  
   * **Assert:** Returns list containing correct JSON schema.  
2. **Tool Loop Logic:**  
   * **Action:** Mock LLM to return ToolCall(name="calc", args={"x": 1}) on first call, and "Answer is 1" on second call.  
   * **Action:** Run CopilotAgent.run("calc 1").  
   * **Assert:** \_execute\_tool\_call was triggered. Loop executed exactly twice.

### **5.2. Integration Tests (Wiring)**

1. **CLI Wiring:**  
   * **Action:** In friday-cli, verify that ToolRegistry is injected into CopilotAgent.

## **6\. Project Scaffolding for Batch 3**

### **6.1. New Directories & Files**

1. **packages/friday-core/**  
   * src/friday\_core/interfaces/tools.py (New: ToolRegistry Protocol).  
2. **packages/friday-llm/**  
   * (Standard files)  
3. **packages/friday-agent/**  
   * src/friday\_agent/profile.py (Updated: Added tools list).  
   * src/friday\_agent/base.py (Updated: Added ToolRegistry usage).  
   * src/friday\_agent/copilot.py (Updated: Implemented Loop).  
4. **apps/friday-cli/**  
   * src/friday\_cli/container.py (Edit: Wire ToolRegistry).

## **7\. The Agentic Memory Loop (The "Meta-Cognition" Layer)**

Architectural Context:  
While AgentBase handles the interaction loop (Thinking \-\> Acting), the memory system must learn from these interactions. This cannot be a simple regex script; it requires cognitive processing.  
This section details how the MemoryExtractor (defined in Batch 2a) uses its own **Shadow Inference** capabilities to transform raw experience into structured knowledge without interrupting the Agent.

### **7.1. The Cognitive Cycle**

The system moves information through four distinct states:

1. **Experience (Episodic):** The raw interaction happens. It is transient and unstructured.  
2. **Reflection (Extraction):** The system "thinks about" the interaction to find facts.  
3. **Learning (Consolidation):** Facts are merged into the Long-Term Graph/Vector stores.  
4. **Recall (Retrieval):** The next time the Agent acts, it retrieves this "Wisdom."

### **7.2. Triggers: When do we learn?**

* **Passive Trigger (The "Background Pulse"):**  
  * **Source:** AgentBase.\_archive\_turn.  
  * **Action:** Fires an async task context\_engine.extract\_context(turn).  
  * **Why:** Ensures the Agent learns from everything it says/hears without explicit effort.  
* **Active Trigger (The "Conscious Note"):**  
  * **Source:** Agent calls scratchpad\_write or store\_fact tool.  
  * **Action:** Immediate, synchronous write to SessionState or GraphStore.  
  * **Why:** Allows the Agent to force-save critical info ("The user's API key is X").

### **7.3. The Extraction Logic (Shadow Inference)**

**IMPORTANT REFACTORING NOTE:** The current MemoryExtractor implementation (`packages/friday-memory/src/friday_memory/context/extractor.py`) calls `litellm.acompletion()` directly. This violates the Dependency Injection principle and must be refactored as part of Batch 3 implementation. The refactored version must:
1. Accept an `LLMClient` via constructor injection
2. Use a specialized "Librarian" AgentProfile (not the main agent's profile)
3. Convert the existing extraction prompt to use the injected LLMClient

**Rationale:** This refactoring ensures testability (mock LLM in tests), consistency with the protocol-first design, and allows using different models for extraction vs. main agent inference.

* **Process:**
  1. **Input:** The raw InteractionTurn (e.g., "User: Deploy to prod").
  2. **Prompting:** The Extractor sends a specific prompt to the LLM via `self.llm.chat_completion()`:
     "Analyze the following interaction. Extract distinct Entities (Nodes) and Relationships (Edges). Output in JSON format conforming to the Friday Graph Schema."
  3. **Parsing:** The Extractor parses the JSON into GraphNode objects.
  4. **Storage:** It calls MemoryController.store\_fact().

### **7.4. The Feedback Loop (Transparency)**

To prevent the Agent from feeling "disconnected" from its own memory:

1. **Feedback Generation:** When store\_fact succeeds, the MemoryController appends a summary string to a temporary buffer.  
2. **Injection:** On the *next* turn, the ContextAssembler reads this buffer.  
3. **Display:** It injects a System Message into the prompt:"System Update: Since your last turn, I automatically archived 2 facts:$$User role is Admin$$  
   ,$$Project is Alpha$$  
   ."  
4. **Result:** The Agent "knows" what it has learned, closing the cognitive loop.

## **8\. Function Calling & Context Strategy (The "Hands")**

Status: Critical Guidance for Implementation  
Role: Defining how costly tools are managed within finite context windows.  
Function calling transforms an LLM from a chatbot into an agent, but it introduces significant "Context Bloat." This section defines the strategies for handling tool definitions and execution history.

### **8.1. The Context Cost Equation (Pinning)**

The ContextAssembler (Batch 2a) must treat Tool Definitions as **Fixed Costs**.

* **Pinning Rule:** Tool definitions (JSON Schemas) are always pinned to the start of the context window (System Block). They are never pruned.  
* The Math:  
  Available\_History\_Tokens \= Total\_Window \- (System\_Prompt \+ Tool\_Definitions \+ Output\_Buffer)  
* **Failure Mode:** If Tool\_Definitions exceed the context limit (unlikely, but possible with hundreds of tools), the Agent must fail at startup with ContextOverflowError.

### **8.2. The Execution History (Pruning)**

The "Tool Loop" (defined in Section 4.3) generates episodic history:  
User \-\> Assistant(Call) \-\> Tool(Result) \-\> Assistant(Response)

* **Pruning Rule:** Unlike Definitions, this history is **Episodic**. It lives in the "Recent History" block.  
* **Loop Amnesia:** In long loops (e.g., 50 steps), early steps *will* be pruned. The Agent might forget it called list\_files 20 turns ago.  
* **Mitigation:** The Agent relies on **Scratchpad State** (Section 8.3) to persist insights across pruned turns.

### **8.3. State Persistence (The "Scratchpad")**

To survive "Loop Amnesia," the Agent must effectively use SessionState.scoped\_vars.

* **Pattern:** Instead of relying on the chat history to remember "File A contains X," the Agent should:  
  1. Call read\_file(A).  
  2. Call scratchpad\_write(key="insight\_A", value="File A contains X").  
* **Context Injection:** The ContextAssembler injects the *entire* Scratchpad content into the **System Block** (Pinned).  
* **Result:** Even if the read\_file event scrolls off the history, the insight\_A remains visible in the System Prompt.

### **8.4. The Re-Act Loop (Architectural Flow)**

The CopilotAgent implementation must strictly follow this cycle to support multi-step reasoning:

1. **Orchestrator:** Calls LLM.chat\_completion with tools.
2. **Observation:** If response.has\_tool\_calls (using ChatCompletionResponse):
   * **Execute:** Run the Python function from ToolRegistry.
   * **Append:** Add the result to messages with role tool.
   * **Recurse:** Jump back to Step 1 (sending the tool output to the LLM).
3. **Termination:** If no tool calls, return the text content to the User.

---

## **9\. Build Plan Rationale & Design Decisions**

This section documents the design decisions made during implementation planning to ensure consistency and traceability.

### **9.1. Specification Updates (January 2026)**

The following updates were made to this specification after review against the existing codebase:

| Issue | Original | Updated | Rationale |
|-------|----------|---------|-----------|
| LLMClient return type | `Union[str, BaseModel]` | `ChatCompletionResponse` | Structured response enables clean tool\_calls checking without hasattr() |
| AgentBase context\_engine type | `ContextAssembler` | `ContextEngineeringInterface` | Protocol-first design; allows pluggable context strategies |
| MemoryExtractor LLM usage | Not specified | Must inject LLMClient | Existing code used litellm directly, violating DI principle |
| Built-in tools | Referenced but undefined | Section 2.4 added | Agents need scratchpad/memory tools to function |
| OpenTelemetryProvider | Stub only | Full implementation | Builders need concrete guidance on OTel SDK usage |
| SessionState in AgentBase | Implicit | Explicit methods added | `_get_scratchpad_context()` provides clear integration pattern |

### **9.2. Key Design Decisions**

1. **ChatCompletionResponse over Union types**
   - Single structured response object with optional tool\_calls
   - Enables `response.has_tool_calls` property for clean control flow
   - Includes usage stats for cost tracking

2. **ChromaVectorStore Refactoring**
   - Current implementation uses litellm directly for embeddings
   - Will be refactored to accept `EmbeddingModel` via constructor
   - Enables testability and provider flexibility

3. **AutonomousAgent Scope**
   - Implemented as minimal stub satisfying ABC contract
   - Full planning/execution logic deferred to future batch
   - Placeholder prevents breaking changes to AgentBase hierarchy

4. **Core Memory Tools**
   - Four built-in tools: scratchpad\_write, scratchpad\_read, recall\_memory, store\_fact
   - Registered automatically with default ToolRegistry
   - Enable the agentic memory loop without custom tool implementation

### **9.3. Implementation Phases**

See `docs/build-plan/batch3buildplan.md` for the complete phased implementation plan including:
- Phase 1: Core Interfaces (LLMClient, EmbeddingModel, ToolRegistry)
- Phase 2: Inference Layer (friday-llm package)
- Phase 3: Observability Enhancement (OpenTelemetryProvider)
- Phase 4: Agent Orchestration (friday-agent package)
- Phase 5: Tool Infrastructure
- Phase 6: Integration & Wiring
- Phase 7: Testing & Validation

### **9.4. Cross-Batch Dependencies**

```
Batch 0 (Core)          ✅ Complete
    ↓
Batch 1 (Data)          ✅ Complete
    ↓
Batch 2 (Memory)        ✅ Complete
    ↓
Batch 2a (Context)      ⚠️ Requires Batch 3 LLMClient for full functionality
    ↓
Batch 3 (Execution)     🔴 This specification
```

**Critical Path:**
- MemoryExtractor (Batch 2a) requires LLMClient (Batch 3 Phase 1)
- ChromaVectorStore (Batch 1) optionally refactored to use EmbeddingModel (Batch 3 Phase 6)
- CopilotAgent requires ToolRegistry + built-in tools (Batch 3 Phases 4-5)
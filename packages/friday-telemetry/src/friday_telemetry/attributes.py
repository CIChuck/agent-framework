"""
OpenTelemetry Attribute Constants.

Provides standardized attribute names following OpenTelemetry semantic
conventions, with Friday-specific extensions.

Ref: https://opentelemetry.io/docs/reference/specs/semconv/gen-ai/
"""


class OTelAttributes:
    """
    OpenTelemetry GenAI semantic convention attribute names.

    These follow the official OpenTelemetry semantic conventions for
    generative AI systems.

    Ref: https://opentelemetry.io/docs/reference/specs/semconv/gen-ai/
    """

    # Operation
    OPERATION_NAME = "gen_ai.operation.name"
    PROVIDER_NAME = "gen_ai.provider.name"

    # Model
    REQUEST_MODEL = "gen_ai.request.model"
    RESPONSE_MODEL = "gen_ai.response.model"

    # Request Parameters
    TEMPERATURE = "gen_ai.request.temperature"
    MAX_TOKENS = "gen_ai.request.max_tokens"
    TOP_P = "gen_ai.request.top_p"

    # Response
    RESPONSE_ID = "gen_ai.response.id"
    FINISH_REASONS = "gen_ai.response.finish_reasons"

    # Usage
    INPUT_TOKENS = "gen_ai.usage.input_tokens"
    OUTPUT_TOKENS = "gen_ai.usage.output_tokens"

    # Conversation
    CONVERSATION_ID = "gen_ai.conversation.id"

    # Embeddings
    EMBEDDINGS_DIMENSION = "gen_ai.embeddings.dimension.count"

    # Error
    ERROR_TYPE = "error.type"

    # Friday-specific extensions (namespaced to avoid conflicts)
    FRIDAY_REQUEST_ID = "friday.request.id"
    FRIDAY_TURN_ID = "friday.turn.id"
    FRIDAY_COST_USD = "friday.cost.usd"
    FRIDAY_TTFT_MS = "friday.streaming.ttft_ms"
    FRIDAY_TOKENS_PER_SEC = "friday.streaming.tokens_per_sec"
    FRIDAY_CHUNK_COUNT = "friday.streaming.chunk_count"
    FRIDAY_ATTEMPT = "friday.retry.attempt"
    FRIDAY_TOTAL_ATTEMPTS = "friday.retry.total_attempts"
    FRIDAY_ERROR_CATEGORY = "friday.error.category"
    FRIDAY_WORKFLOW_ID = "friday.workflow.id"
    FRIDAY_EXECUTION_ID = "friday.execution.id"
    FRIDAY_PIPELINE_ID = "friday.pipeline.id"
    FRIDAY_TASK_ID = "friday.task.id"
    FRIDAY_ASSIGNMENT_ID = "friday.assignment.id"
    FRIDAY_AGENT_ID = "friday.agent.id"
    FRIDAY_LLM_SERVICE = "friday.llm.service"


class FridayMemoryAttributes:
    """Friday memory-specific OpenTelemetry attributes."""

    # Memory operations
    MEMORY_OPERATION = "friday.memory.operation"
    MEMORY_STORE_TYPE = "friday.memory.store_type"
    MEMORY_DOCUMENT_COUNT = "friday.memory.document_count"
    MEMORY_TOTAL_CHARS = "friday.memory.total_chars"

    # Recall specifics
    MEMORY_QUERY_TOKENS = "friday.memory.query_tokens"
    MEMORY_RESULTS_COUNT = "friday.memory.results_count"
    MEMORY_CACHE_HIT = "friday.memory.cache_hit"
    MEMORY_RERANKING_APPLIED = "friday.memory.reranking_applied"

    # Timing breakdown
    MEMORY_VECTOR_SEARCH_MS = "friday.memory.vector_search_ms"
    MEMORY_GRAPH_TRAVERSAL_MS = "friday.memory.graph_traversal_ms"
    MEMORY_EMBEDDING_MS = "friday.memory.embedding_ms"

    # Maintenance
    MEMORY_ITEMS_PROCESSED = "friday.memory.items_processed"
    MEMORY_ITEMS_AFFECTED = "friday.memory.items_affected"


class FridayToolAttributes:
    """Friday tool execution attributes."""

    # Tool operations
    TOOL_NAME = "friday.tool.name"
    TOOL_CATEGORY = "friday.tool.category"
    TOOL_EXECUTION_MS = "friday.tool.execution_ms"
    TOOL_SUCCESS = "friday.tool.success"
    TOOL_ERROR_TYPE = "friday.tool.error_type"


class FridayAgentAttributes:
    """Friday agent decision attributes."""

    # Agent operations
    AGENT_NAME = "friday.agent.name"
    AGENT_ITERATION = "friday.agent.iteration"
    AGENT_ACTION = "friday.agent.action"
    AGENT_REASONING_TOKENS = "friday.agent.reasoning_tokens"

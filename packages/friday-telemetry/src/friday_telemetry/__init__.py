"""
Friday Telemetry Package.

Unified telemetry for the Friday framework, providing consistent
observability across LLM, memory, and tool operations.

Components:
- TelemetryInterface: Abstract protocol for telemetry providers
- Providers: DebugTelemetryRecorder, OpenTelemetryProvider, CompositeProvider
- Models: LLM, Memory, and common telemetry data models
- Helpers: Context managers for tracking operations
- Attributes: OpenTelemetry semantic convention constants

Example:
    from friday_telemetry import (
        DebugTelemetryRecorder,
        LLMTelemetryHelper,
        MemoryTelemetryHelper,
    )

    # Create a debug recorder for testing
    recorder = DebugTelemetryRecorder()

    # Track LLM operations
    llm_helper = LLMTelemetryHelper(telemetry=recorder)
    with llm_helper.track_completion(model="gpt-4") as tracker:
        response = await llm.complete(messages)
        tracker.set_response(usage=TokenUsage.from_response(response.usage))

    # Track memory operations
    memory_helper = MemoryTelemetryHelper(telemetry=recorder)
    with memory_helper.track_recall(operation="search", query_text="test") as tracker:
        results = await memory.search("test")
        tracker.set_results(results_count=len(results))
"""

# Interface
# Attributes
from friday_telemetry.attributes import (
    FridayAgentAttributes,
    FridayMemoryAttributes,
    FridayToolAttributes,
    OTelAttributes,
)

# Config
from friday_telemetry.config import OTelConfig, TelemetryConfig, TelemetryFactoryConfig
from friday_telemetry.factory import ManagedTelemetry, create_telemetry

# Helpers
from friday_telemetry.helpers import (
    CompletionTracker,
    EmbeddingTracker,
    LLMTelemetryHelper,
    MaintenanceTracker,
    MemoryRecallTracker,
    MemoryTelemetryHelper,
    MemoryWriteTracker,
    StreamingTracker,
    classify_error,
)
from friday_telemetry.helpers.correlation import CorrelationScope, ExecutionContext
from friday_telemetry.helpers.mcp import MCPTelemetryHelper, opaque_mcp_ref
from friday_telemetry.helpers.safe_llm import SafeLLMTelemetry
from friday_telemetry.interface import TelemetryInterface
from friday_telemetry.lifecycle import (
    LifecycleResult,
    TelemetryInitializationError,
    TelemetryLifecycle,
    TelemetryOperationError,
    TelemetrySnapshot,
)

# Models - Common
from friday_telemetry.models.common import RequestContext
from friday_telemetry.models.execution import ExecutionEvent

# Models - LLM
from friday_telemetry.models.llm import (
    ConversationContext,
    CostEstimate,
    EmbeddingMetrics,
    ErrorCategory,
    GenAIOperationType,
    LLMCallMetrics,
    StreamingMetrics,
    TokenUsage,
)
from friday_telemetry.models.llm_events import LLMEvent
from friday_telemetry.models.mcp import MCPEvent, MCPEventName, MCPEventReason

# Models - Memory
from friday_telemetry.models.memory import (
    ArbitrationOpsMetrics,
    MaintenanceMetrics,
    MemoryRecallMetrics,
    MemoryWriteMetrics,
)

# Providers
from friday_telemetry.providers import (
    CompositeProvider,
    DebugTelemetryRecorder,
    OpenTelemetryProvider,
)

# Records
from friday_telemetry.records import EventRecord, SpanRecord

__all__ = [
    "CorrelationScope",
    "ExecutionContext",
    "ExecutionEvent",
    "LLMEvent",
    "SafeLLMTelemetry",
    # Interface
    "TelemetryInterface",
    # Records
    "SpanRecord",
    "EventRecord",
    # Providers
    "DebugTelemetryRecorder",
    "OpenTelemetryProvider",
    "CompositeProvider",
    # Models - Common
    "RequestContext",
    # Models - LLM
    "GenAIOperationType",
    "ErrorCategory",
    "TokenUsage",
    "CostEstimate",
    "StreamingMetrics",
    "ConversationContext",
    "LLMCallMetrics",
    "EmbeddingMetrics",
    # Models - Memory
    "MemoryWriteMetrics",
    "MemoryRecallMetrics",
    "MaintenanceMetrics",
    "ArbitrationOpsMetrics",
    # Models and helpers - MCP
    "MCPEvent",
    "MCPEventName",
    "MCPEventReason",
    "MCPTelemetryHelper",
    "opaque_mcp_ref",
    # Attributes
    "OTelAttributes",
    "FridayMemoryAttributes",
    "FridayToolAttributes",
    "FridayAgentAttributes",
    # Helpers
    "LLMTelemetryHelper",
    "StreamingTracker",
    "CompletionTracker",
    "EmbeddingTracker",
    "classify_error",
    "MemoryTelemetryHelper",
    "MemoryWriteTracker",
    "MemoryRecallTracker",
    "MaintenanceTracker",
    # Config
    "TelemetryConfig",
    "OTelConfig",
    "TelemetryFactoryConfig",
    "ManagedTelemetry",
    "create_telemetry",
    "TelemetryLifecycle",
    "LifecycleResult",
    "TelemetrySnapshot",
    "TelemetryInitializationError",
    "TelemetryOperationError",
]

__version__ = "0.1.0a4"

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
from friday_telemetry.config import TelemetryConfig

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
from friday_telemetry.interface import TelemetryInterface

# Models - Common
from friday_telemetry.models.common import RequestContext

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
]

__version__ = "0.1.0a1"

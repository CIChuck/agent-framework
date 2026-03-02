---
title: "Debugging Strategies"
description: "Use structured logs, memory inspection, and replay to diagnose agent behavior."
weight: 2
---

Diagnose unexpected agent behavior by reading structured logs at the appropriate level, inspecting memory store state, and replaying conversation transcripts step by step.

## Logging Configuration

### Basic Setup

Configure the root logger and all Friday package loggers at once:

```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/friday/agent.log')
    ]
)

friday_loggers = [
    'friday_core',
    'friday_memory',
    'friday_llm',
    'friday_agent',
    'friday_tools',
]

for logger_name in friday_loggers:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
```

### Component-Specific Logging

Enable verbose logging for individual subsystems without flooding the entire console:

```python
# Memory: retrieval, storage, lifecycle
logging.getLogger('friday_memory.context').setLevel(logging.DEBUG)
logging.getLogger('friday_memory.lifecycle').setLevel(logging.INFO)
logging.getLogger('friday_memory.adapters').setLevel(logging.DEBUG)

# LLM: requests, responses, token counts
logging.getLogger('friday_llm.service').setLevel(logging.DEBUG)
logging.getLogger('friday_llm.circuit_breaker').setLevel(logging.INFO)

# Agent: Re-Act loop, tool calls
logging.getLogger('friday_agent.copilot').setLevel(logging.DEBUG)
logging.getLogger('friday_agent.tools').setLevel(logging.DEBUG)

# Tool execution details
logging.getLogger('friday_tools').setLevel(logging.DEBUG)
```

### Structured JSON Logging

For production environments and log aggregators (Datadog, Splunk, ELK):

```python
import json
import logging

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_data['session_id'] = record.session_id
        if hasattr(record, 'token_count'):
            log_data['token_count'] = record.token_count

        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(StructuredFormatter())
logging.getLogger().addHandler(handler)
```

### Contextual Logging with LoggerAdapter

Automatically attach session and user context to every log line:

```python
class AgentLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get('extra', {})
        extra.update({
            'session_id': self.extra['session_id'],
            'user_id': self.extra['user_id'],
            'agent_name': self.extra['agent_name']
        })
        kwargs['extra'] = extra
        return msg, kwargs

adapter = AgentLoggerAdapter(
    logger,
    {
        'session_id': session_id,
        'user_id': user_id,
        'agent_name': 'CopilotAgent'
    }
)

adapter.info("Processing user query")  # Session context included automatically
```

### Performance Logging

Wrap any operation with this context manager to record its duration:

```python
import time
from contextlib import contextmanager

@contextmanager
def log_performance(operation_name: str, logger: logging.Logger):
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        logger.info(
            f"{operation_name} completed",
            extra={'duration_ms': duration * 1000}
        )

with log_performance("context_assembly", logger):
    context_payload = await context_engine.assemble_context(...)
```

---

## Log Analysis

### Trace a Specific Session

```bash
# Find all logs for a specific session
grep "session_abc123" agent.log | less

# Trace a specific request
grep "request_id_xyz" agent.log | \
  awk '{print $1, $2, $4, $5}' | \
  column -t
```

### Identify Performance Bottlenecks

```bash
# Extract slowest operations from JSON logs
grep "duration_ms" agent.log | \
  jq -r '[.operation, .duration_ms] | @csv' | \
  sort -t',' -k2 -rn | \
  head -20
```

Sample output:
```
"context_assembly",3456.7
"llm_call",2890.3
"memory_retrieval",1234.5
```

### Find Errors and Stack Traces

```bash
# Count errors by type
grep "ERROR" agent.log | \
  sed 's/.*ERROR] //' | \
  sed 's/:.*//' | \
  sort | uniq -c | sort -rn

# Show full stack traces
grep -A 20 "Traceback" agent.log
```

### Monitor Token Usage

```bash
# Total tokens used across all requests
grep "token_count" agent.log | \
  jq '.token_count' | \
  awk '{sum+=$1} END {print "Total tokens:", sum}'

# Average tokens per request
grep "token_count" agent.log | \
  jq '.token_count' | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count}'
```

---

## Interactive Debugging

### CLI Debug Mode

```bash
# Start the CLI in debug mode
friday-cli --debug

# Available debug commands:
/debug memory          # Show current memory state
/debug context         # Show last context payload
/debug tokens          # Show token usage breakdown
/debug tools           # List registered tools
/debug session         # Show session information
/debug llm             # Show LLM configuration
```

Example output from `/debug memory`:

```
Memory State:
  Vector Store: 156 insights
    - Short-term: 23
    - Long-term: 98
    - Decayed: 35
  Graph Store: 89 entities, 234 relationships
  Episodic Store: 45 conversation turns

Last Maintenance:
  Decay cycle: 2 hours ago
  Promotion cycle: 6 hours ago
```

### Python Debugger

```python
import pdb

class CopilotAgent(AgentBase):
    async def run(self, input_signal: str):
        context_payload = await self.context_engine.assemble_context(...)

        pdb.set_trace()  # Breakpoint
        # (Pdb) p context_payload.total_tokens
        # (Pdb) p len(context_payload.insights)
        # (Pdb) p [e.name for e in context_payload.entities]

        messages = await self.context_engine.format_prompt(...)
        return await self._execute_loop(messages)
```

### VS Code Launch Configuration

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Friday Agent",
            "type": "python",
            "request": "launch",
            "module": "friday_cli",
            "args": ["chat"],
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}",
                "LOG_LEVEL": "DEBUG"
            },
            "justMyCode": false
        }
    ]
}
```

---

## Transcript Analysis

The transcript system records every interaction for replay and analysis.

### Exporting Transcripts

```python
from friday_memory.adapters.episodic import TranscriptStoreAdapter

adapter = TranscriptStoreAdapter(db_path="~/.friday/memory/transcript.db")

# Export to JSONL for machine analysis
await adapter.export_jsonl(
    output_path="/tmp/transcript.jsonl",
    session_id="optional_filter",
    start_date="2026-01-01",
    end_date="2026-01-31"
)

# Export to Markdown for human review
await adapter.export_markdown(
    output_path="/tmp/transcript.md",
    session_id="session_123"
)
```

### Analyzing Tool Usage

```python
import json
from collections import Counter

with open('/tmp/transcript.jsonl') as f:
    turns = [json.loads(line) for line in f]

tool_calls = []
for turn in turns:
    if turn.get('tool_calls'):
        tool_calls.extend([tc['name'] for tc in turn['tool_calls']])

tool_usage = Counter(tool_calls)
print("Most used tools:")
for tool, count in tool_usage.most_common(10):
    print(f"  {tool}: {count}")
```

### Detecting Failure Patterns

```python
failures = [t for t in turns if t.get('error')]

print(f"Found {len(failures)} failed turns")
for failure in failures:
    print(f"Timestamp: {failure['timestamp']}")
    print(f"Error: {failure['error']}")
    print(f"Query: {failure['user_message'][:100]}...")

error_types = Counter([f['error'].split(':')[0] for f in failures])
print("\nError distribution:")
for error_type, count in error_types.most_common():
    print(f"  {error_type}: {count}")
```

---

## Telemetry Integration

### OpenTelemetry with Jaeger

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

async def instrumented_run(agent, query: str):
    with tracer.start_as_current_span("agent_run") as span:
        span.set_attribute("query_length", len(query))

        with tracer.start_as_current_span("context_assembly"):
            context = await agent.context_engine.assemble_context(...)
            span.set_attribute("context_tokens", context.total_tokens)

        with tracer.start_as_current_span("llm_call"):
            response = await agent.llm.chat_completion(...)
            span.set_attribute("response_tokens", response.usage.total_tokens)

        return response
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

agent_requests = Counter(
    'friday_agent_requests_total',
    'Total agent requests',
    ['agent_name', 'status']
)

agent_latency = Histogram(
    'friday_agent_latency_seconds',
    'Agent request latency',
    ['agent_name']
)

async def monitored_agent_run(agent, query: str):
    start = time.time()
    try:
        response = await agent.run(query)
        agent_requests.labels(agent_name='copilot', status='success').inc()
        return response
    except Exception as e:
        agent_requests.labels(agent_name='copilot', status='error').inc()
        raise
    finally:
        agent_latency.labels(agent_name='copilot').observe(time.time() - start)

# Expose metrics at http://localhost:8000/metrics
start_http_server(8000)
```

---

## Performance Profiling

### Finding Slow Functions with cProfile

```python
import cProfile
import pstats
from pstats import SortKey

profiler = cProfile.Profile()
profiler.enable()

response = await agent.run("What's the weather?")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats(SortKey.CUMULATIVE)
stats.print_stats(20)

# Output shows:
# ncalls  tottime  cumtime filename:lineno(function)
#    1    0.001    2.456 copilot.py:50(run)
#    1    0.123    1.234 context.py:100(assemble_context)
```

### Cost Monitoring

```python
from friday_llm.pricing import TokenPriceCalculator
from datetime import datetime, timedelta

class CostMonitor:
    def __init__(self, daily_budget: float):
        self.daily_budget = daily_budget
        self.daily_usage = 0.0
        self.reset_time = datetime.now()

    def track_request(self, cost: float):
        if datetime.now() - self.reset_time > timedelta(days=1):
            self.daily_usage = 0.0
            self.reset_time = datetime.now()

        self.daily_usage += cost

        if self.daily_usage > self.daily_budget:
            raise RuntimeError(
                f"Daily budget exceeded: ${self.daily_usage:.2f} > ${self.daily_budget:.2f}"
            )
        elif self.daily_usage > self.daily_budget * 0.8:
            logger.warning(f"Budget at 80%: ${self.daily_usage:.2f} used")

monitor = CostMonitor(daily_budget=10.0)
```

## Related Pages

- [Common Issues](/docs/troubleshooting/common-issues/) — Step-by-step solutions for the most common errors
- [FAQ](/docs/troubleshooting/faq/) — General questions about Friday
- [Performance Optimization](/docs/advanced/performance/) — Token budgets, caching, and concurrency

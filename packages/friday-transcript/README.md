# Friday Transcript

Conversation records, SQLite/JSONL stores, and CSV, JSONL and Markdown exporters. Use transcripts for session history and inspection; use Friday Memory for extraction, semantic recall and context assembly.

**Distribution:** [friday-framework-transcript](https://pypi.org/project/friday-framework-transcript/) · **Import:** `friday_transcript`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-transcript==0.1.0a4"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: persist a conversation

```python
import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

from friday_transcript import SQLiteTranscriptStore, TranscriptEntry, TranscriptSession

async def main() -> None:
    with TemporaryDirectory() as directory:
        store = SQLiteTranscriptStore(Path(directory) / "transcript.db")
        await store.create_session(
            TranscriptSession(session_id="demo", model_name="offline-example")
        )
        await store.append_entry(
            TranscriptEntry(
                id="entry-1", session_id="demo", turn_number=1,
                user_message="Hello", assistant_message="Hello from Friday",
            )
        )
        entries = await store.get_entries("demo")
        print(entries[0].assistant_message)

asyncio.run(main())
```

Expected output: `Hello from Friday`. The temporary database is removed when the example exits. Supply an application-owned persistent path to retain it.

## Records and storage

- `TranscriptSession` identifies a session and its configuration/aggregates.
- `TranscriptEntry` records a turn, including optional tool, usage, timing and provenance fields.
- `SQLiteTranscriptStore` supports querying and snapshot/recovery workflows; `JSONLTranscriptStore` provides a file-oriented alternative.
- Exporters create portable views. Exporting records is separate from semantic-memory ingestion.

Transcripts can contain prompts, responses, tool results and configuration snapshots. They are not covered by content-free telemetry guarantees. Apply your own retention, access and redaction policy. Coordinate maintenance through the public quiescence/snapshot contracts rather than copying or replacing a live database.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
There is no package-local test suite yet. Start with an import check:

```bash
uv run --no-sync python -c "import friday_transcript"
```

SQLite behavior is also exercised by Runtime and Chat integration tests. Run the relevant consumer suite when changing persisted records or store contracts.
## Documentation and support

[Memory integration](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-memory/README.md) · [Runtime integration](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-runtime/README.md) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-transcript/src/friday_transcript) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).

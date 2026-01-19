from __future__ import annotations

from typing import Any
from pathlib import Path
from pydantic import BaseModel, Field

from friday_tools.base import FridayTool, ToolResult
from friday_transcript import SQLiteTranscriptStore, CSVExporter, JSONLExporter, MarkdownExporter

class TranscriptTool(FridayTool):
    """
    Export or view conversation transcripts.
    """
    name = "transcript_tool"
    description = "Export conversation logs to files (CSV, JSONL, Markdown)."
    
    class Input(BaseModel):
        action: str = Field(..., description="'export_all' or 'export_session'")
        format: str = Field("markdown", description="Format: markdown, jsonl, csv")
        session_id: str | None = Field(None, description="Session ID (required for export_session)")
        output_dir: str = Field("./exports", description="Directory to save files")

    def __init__(self, store: SQLiteTranscriptStore):
        self.store = store

    async def run(self, args: Input) -> ToolResult:
        out_path = Path(args.output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        if args.action == "export_all":
            if args.format != "csv":
                return ToolResult(content="Error: export_all only supports CSV currently.", error="Invalid format")
            
            exporter = CSVExporter(self.store)
            counts = await exporter.export_all_sessions(out_path)
            return ToolResult(
                content=f"Exported all sessions to {out_path}",
                data=counts
            )

        elif args.action == "export_session":
            if not args.session_id:
                return ToolResult(content="Error: session_id required.", error="Missing session_id")
            
            file_path = out_path / f"transcript_{args.session_id}.{args.format}"
            count = 0
            
            if args.format == "jsonl":
                exporter = JSONLExporter(self.store)
                count = await exporter.export_session(args.session_id, file_path)
            elif args.format == "markdown":
                exporter = MarkdownExporter(self.store)
                count = await exporter.export_session(args.session_id, file_path)
            else:
                return ToolResult(content=f"Error: Format {args.format} not supported for session export.", error="Invalid format")

            return ToolResult(
                content=f"Exported {count} entries to {file_path}",
                data={"count": count, "path": str(file_path)}
            )

        return ToolResult(content="Invalid action.", error="Invalid action")

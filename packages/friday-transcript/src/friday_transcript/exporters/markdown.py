"""
Markdown transcript exporter.

Exports transcripts to human-readable Markdown format for documentation,
review, and sharing.
"""

from pathlib import Path
from typing import TextIO

from friday_transcript.models.transcript import TranscriptEntry, TranscriptSession
from friday_transcript.stores.protocol import TranscriptStore


class MarkdownExporter:
    """
    Export transcripts to Markdown format.

    Creates human-readable Markdown documents with conversation turns,
    metadata, and optional metrics. Useful for:
    - Documentation
    - Code review discussions
    - Sharing conversations
    - Training dataset review
    """

    def __init__(
        self,
        store: TranscriptStore,
        user_name: str = "User",
        assistant_name: str = "Assistant",
    ) -> None:
        """
        Initialize the Markdown exporter.

        Args:
            store: Transcript store to export from
            user_name: Display name for user messages
            assistant_name: Display name for assistant messages
        """
        self._store = store
        self.user_name = user_name
        self.assistant_name = assistant_name

    async def export_session(
        self,
        session_id: str,
        output: Path | TextIO,
        include_metrics: bool = True,
        include_tool_calls: bool = False,
        include_timestamps: bool = True,
    ) -> int:
        """
        Export a session to Markdown format.

        Args:
            session_id: Session to export
            output: Output file path or file-like object
            include_metrics: Include token counts and latency
            include_tool_calls: Include tool call details
            include_timestamps: Include timestamps for each turn

        Returns:
            Number of entries exported
        """
        # Get session and entries
        session = await self._store.get_session(session_id)
        entries = await self._store.get_entries(session_id, limit=100000)

        # Open file if path provided
        should_close = False
        if isinstance(output, Path):
            f = open(output, "w")
            should_close = True
        else:
            f = output

        try:
            # Write header
            f.write(self._render_header(session, len(entries)))

            # Write entries
            for entry in entries:
                f.write(
                    self._render_entry(
                        entry,
                        include_metrics=include_metrics,
                        include_tool_calls=include_tool_calls,
                        include_timestamps=include_timestamps,
                    )
                )

            # Write footer with summary
            if session and include_metrics:
                f.write(self._render_footer(session))

            return len(entries)
        finally:
            if should_close:
                f.close()

    def _render_header(
        self, session: TranscriptSession | None, entry_count: int
    ) -> str:
        """Render the document header."""
        lines = []

        if session:
            lines.append(f"# Session: {session.session_id}\n")
            lines.append("")
            lines.append(f"**Started:** {session.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if session.ended_at:
                lines.append(
                    f"**Ended:** {session.ended_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            lines.append(f"**Model:** {session.model_name}")
            lines.append(f"**Turns:** {entry_count}")
            lines.append("")

            if session.system_prompt:
                lines.append("## System Prompt")
                lines.append("")
                lines.append("```")
                lines.append(session.system_prompt)
                lines.append("```")
                lines.append("")

            lines.append("---")
            lines.append("")
        else:
            lines.append("# Transcript")
            lines.append("")

        return "\n".join(lines)

    def _render_entry(
        self,
        entry: TranscriptEntry,
        include_metrics: bool = True,
        include_tool_calls: bool = False,
        include_timestamps: bool = True,
    ) -> str:
        """Render a single entry."""
        lines = []

        # Turn header
        header_parts = [f"## Turn {entry.turn_number}"]
        if include_timestamps:
            header_parts.append(f"[{entry.timestamp.strftime('%H:%M:%S')}]")
        lines.append(" ".join(header_parts))
        lines.append("")

        # User message
        if entry.user_message:
            lines.append(f"**{self.user_name}:**")
            lines.append("")
            lines.append(entry.user_message)
            lines.append("")

        # Tool calls (if requested and present)
        if include_tool_calls and entry.tool_calls:
            lines.append("**Tool Calls:**")
            lines.append("")
            for tc in entry.tool_calls:
                lines.append(f"- `{tc.name}`: `{tc.arguments}`")
            lines.append("")

            if entry.tool_results:
                lines.append("**Tool Results:**")
                lines.append("")
                for tr in entry.tool_results:
                    if tr.error:
                        lines.append(f"- Error: {tr.error}")
                    else:
                        output_preview = str(tr.output)[:200]
                        if len(str(tr.output)) > 200:
                            output_preview += "..."
                        lines.append(f"- {output_preview}")
                lines.append("")

        # Assistant message
        if entry.assistant_message:
            lines.append(f"**{self.assistant_name}:**")
            lines.append("")
            lines.append(entry.assistant_message)
            lines.append("")

        # Metrics
        if include_metrics:
            metrics = []
            if entry.total_tokens:
                metrics.append(f"Tokens: {entry.total_tokens}")
            if entry.latency_ms:
                metrics.append(f"Latency: {entry.latency_ms:.0f}ms")
            if entry.model_name:
                metrics.append(f"Model: {entry.model_name}")

            if metrics:
                lines.append(f"*{' | '.join(metrics)}*")
                lines.append("")

        lines.append("---")
        lines.append("")

        return "\n".join(lines)

    def _render_footer(self, session: TranscriptSession) -> str:
        """Render the document footer with summary statistics."""
        lines = []

        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total Turns:** {session.total_turns}")
        lines.append(f"- **Total Tokens:** {session.total_tokens}")
        lines.append(f"- **Total Latency:** {session.total_latency_ms:.0f}ms")

        if session.total_turns > 0:
            avg_tokens = session.total_tokens / session.total_turns
            avg_latency = session.total_latency_ms / session.total_turns
            lines.append(f"- **Avg Tokens/Turn:** {avg_tokens:.0f}")
            lines.append(f"- **Avg Latency/Turn:** {avg_latency:.0f}ms")

        lines.append("")

        return "\n".join(lines)

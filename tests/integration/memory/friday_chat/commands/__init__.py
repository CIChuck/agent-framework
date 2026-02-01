"""
Command handlers for Friday Chat.

Commands are organized by category:
- session_cmds: clear, cls, exit
- memory_cmds: history, memory, context, prompt, debug, entities, facts, etc.
- transcript_cmds: sessions, transcript, export
- maintenance_cmds: reset, reorganize, lifecycle, migrate
- tools_cmds: tools, run-tool, inject-tools, recommend-tools, tool-budget
- orchestration_cmds: switch, agents, agent, delegate, status
- workflow_cmds: workflow subcommands
- file_cmds: read, ingest
"""

from .session_cmds import register_session_commands
from .memory_cmds import register_memory_commands
from .transcript_cmds import register_transcript_commands
from .maintenance_cmds import register_maintenance_commands
from .tools_cmds import register_tools_commands
from .orchestration_cmds import register_orchestration_commands
from .workflow_cmds import register_workflow_commands
from .file_cmds import register_file_commands


def register_all_commands(registry, session) -> None:
    """Register all command handlers with the registry."""
    register_session_commands(registry, session)
    register_memory_commands(registry, session)
    register_transcript_commands(registry, session)
    register_maintenance_commands(registry, session)
    register_tools_commands(registry, session)
    register_orchestration_commands(registry, session)
    register_workflow_commands(registry, session)
    register_file_commands(registry, session)


__all__ = [
    "register_all_commands",
    "register_session_commands",
    "register_memory_commands",
    "register_transcript_commands",
    "register_maintenance_commands",
    "register_tools_commands",
    "register_orchestration_commands",
    "register_workflow_commands",
    "register_file_commands",
]

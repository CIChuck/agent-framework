from __future__ import annotations

from typing import Literal

from friday_memory import MemoryController, SessionState
from pydantic import BaseModel, Field

from friday_tools.base import FridayTool, ToolResult


class MemoryStatsTool(FridayTool):
    """
    Get statistics about the current memory session.
    """

    name = "memory_stats"
    description = "Get statistics about current session turns and variables."

    class Input(BaseModel):
        session_id: str = Field(..., description="The ID of the session to inspect")

    def __init__(
        self, controller: MemoryController, session_state: SessionState | None = None
    ):
        self.controller = controller
        self.session_state = session_state

    async def run(self, args: Input) -> ToolResult:
        turn_count = self.session_state.turn_count if self.session_state else 0
        var_count = len(self.session_state.scoped_vars) if self.session_state else 0

        # We could fetch more stats from controller if needed

        content = (
            f"Session ID: {args.session_id}\n"
            f"Turns in session: {turn_count}\n"
            f"Scoped variables: {var_count}"
        )

        return ToolResult(
            content=content,
            data={
                "session_id": args.session_id,
                "turn_count": turn_count,
                "variable_count": var_count,
                "variables": self.session_state.scoped_vars
                if self.session_state
                else {},
            },
        )


class GraphInspectionTool(FridayTool):
    """
    Inspect entities and relationships in the Knowledge Graph.
    """

    name = "graph_inspect"
    description = "List nodes and edges from the Knowledge Graph."

    class Input(BaseModel):
        limit: int = Field(500, description="Maximum number of items to return")
        node_type: str | None = Field(
            None, description="Filter nodes by type (e.g. 'Person', 'Project')"
        )

    def __init__(self, controller: MemoryController):
        self.controller = controller

    async def run(self, args: Input) -> ToolResult:
        nodes = await self.controller.graph.get_all_nodes()
        edges = await self.controller.graph.get_all_edges()

        # Filter logic
        if args.node_type:
            nodes = [n for n in nodes if n.type == args.node_type]

        # Apply limits
        nodes = nodes[: args.limit]
        edges = edges[: args.limit]

        # Build text representation
        lines = []
        if nodes:
            lines.append(f"Entities ({len(nodes)}):")
            for node in nodes:
                lines.append(f"  - {node.label} ({node.type})")

        if edges:
            lines.append(f"Relationships ({len(edges)}):")
            node_lookup = {n.id: n.label for n in nodes}
            for edge in edges:
                src = node_lookup.get(edge.source_id, edge.source_id[:8])
                tgt = node_lookup.get(edge.target_id, edge.target_id[:8])
                lines.append(f"  {src} --[{edge.relation}]--> {tgt}")

        return ToolResult(
            content="\n".join(lines) if lines else "Graph is empty.",
            data={
                "nodes": [n.model_dump() for n in nodes],
                "edges": [e.model_dump() for e in edges],
            },
            metadata={"node_count": len(nodes), "edge_count": len(edges)},
        )


class VectorInspectionTool(FridayTool):
    """
    Inspect documents (facts, insights, summaries) in the Vector Store.
    """

    name = "vector_inspect"
    description = "List documents from the Vector Store, optionally filtered by type."

    class Input(BaseModel):
        limit: int = Field(100, description="Maximum number of documents to return")
        doc_type: Literal["insight", "summary", "meta_insight", "all"] = Field(
            "all", description="Type of document to retrieve"
        )
        query: str | None = Field(None, description="Optional semantic search query")

    def __init__(self, controller: MemoryController):
        self.controller = controller

    async def run(self, args: Input) -> ToolResult:
        where_filter = {}
        if args.doc_type != "all":
            where_filter["type"] = args.doc_type

        # Execute Query (either Search or GetAll)
        if args.query:
            # Semantic search
            results = await self.controller.vector.search(
                query=args.query, limit=args.limit, where=where_filter
            )
            # Normalize search results (list of dicts) to list of docs
            documents = results  # search returns list of dicts with 'text', 'metadata', 'distance'  # noqa: E501
        else:
            # Get All
            documents = await self.controller.vector.get_all(
                limit=args.limit, where=where_filter if where_filter else None
            )

        # Build text representation
        lines = []
        for i, doc in enumerate(documents, 1):
            text = doc.get("text", "")[:200].replace("\n", " ")
            meta = doc.get("metadata", {})
            lines.append(f"{i}. [{meta.get('type', 'unknown')}] {text}...")

        return ToolResult(
            content="\n".join(lines) if lines else "No documents found.",
            data={"documents": documents},
            metadata={"count": len(documents), "filter": args.doc_type},
        )

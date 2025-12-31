"""
Abstract Base Classes for Data Storage Adapters.
Includes VectorStoreAdapter, GraphStoreAdapter, and EpisodicStoreAdapter protocols.

Ref: Batch 1 Specification, Section 1

Note: Type references like 'InteractionTurn', 'GraphNode', 'GraphEdge' are forward
references to models that will be defined in friday-memory/models/. This allows
the protocols to be defined without circular imports.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Forward references to types defined in friday-memory/models/
    # These are only used for type checking, not at runtime
    from typing import TypeAlias

    InteractionTurn: TypeAlias = Any  # Will be friday_memory.models.InteractionTurn
    GraphNode: TypeAlias = Any  # Will be friday_memory.models.GraphNode
    GraphEdge: TypeAlias = Any  # Will be friday_memory.models.GraphEdge


class EpisodicStoreAdapter(ABC):
    """
    Protocol for short-term conversation history storage.

    Handles the "Thread" of interactions for a session. Critical for
    the Context Engineering extraction cycle.

    Implementations might use: JSON files, SQLite, Redis, etc.
    """

    @abstractmethod
    async def add_turn(self, session_id: str, turn: "InteractionTurn") -> bool:
        """
        Logs a single user/assistant interaction.

        Args:
            session_id: Unique session identifier
            turn: The interaction turn to store

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_turns(
        self, session_id: str, limit: int = 10, offset: int = 0
    ) -> list["InteractionTurn"]:
        """
        Retrieves chronological history for context injection.

        Args:
            session_id: Unique session identifier
            limit: Maximum number of turns to retrieve
            offset: Number of turns to skip (for pagination)

        Returns:
            List of interaction turns, ordered chronologically
        """
        pass

    @abstractmethod
    async def get_unconsolidated_turns(
        self, session_id: str
    ) -> list["InteractionTurn"]:
        """
        Retrieves turns that have NOT yet been processed by the Memory Consolidator.

        Used by the 'Extraction' cycle to identify new information
        that needs to be analyzed and potentially stored in long-term memory.

        Args:
            session_id: Unique session identifier

        Returns:
            List of unprocessed interaction turns
        """
        pass

    @abstractmethod
    async def mark_consolidated(self, turn_ids: list[str]) -> bool:
        """
        Marks specific turns as 'processed' so they aren't re-extracted.

        Called after the Memory Consolidator has processed the turns
        and extracted relevant facts/entities.

        Args:
            turn_ids: List of turn IDs to mark as consolidated

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def rewind_history(self, session_id: str, target_turn_id: str) -> bool:
        """
        Hard Reset: Deletes all interaction turns *after* the target_turn_id.

        Used to recover from 'death spirals' or logic errors. Provides
        Google ADK-style "time travel" capability.

        Args:
            session_id: Unique session identifier
            target_turn_id: The turn ID to rewind to (this turn is kept)

        Returns:
            True if successful, False otherwise
        """
        pass


class VectorStoreAdapter(ABC):
    """
    Protocol for semantic search storage.

    Handles embedding and retrieval of document chunks for
    similarity-based search.

    Implementations might use: ChromaDB, FAISS, Pinecone, etc.
    """

    @abstractmethod
    async def add_documents(
        self, texts: list[str], metadatas: list[dict[str, Any]], ids: list[str]
    ) -> bool:
        """
        Embeds and stores raw text using the internal embedding model.

        Args:
            texts: List of text chunks to embed and store
            metadatas: List of metadata dicts (must include provenance)
            ids: List of unique document IDs

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: dict[str, Any] | None = None,
        rerank: bool = False,
        hybrid: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Performs semantic retrieval on stored documents.

        Args:
            query_text: The search query
            n_results: Maximum number of results to return
            where: Optional metadata filter (e.g., {'source_type': 'document'})
            rerank: If True, apply reranking to improve result quality
            hybrid: If True, combine semantic and keyword search

        Returns:
            List of result dicts containing text, metadata, and similarity scores
        """
        pass

    @abstractmethod
    async def delete(self, ids: list[str]) -> bool:
        """
        Removes documents by ID.

        Args:
            ids: List of document IDs to delete

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def delete_where(self, where: dict[str, Any]) -> int:
        """
        Removes documents matching a metadata filter.

        Essential for time-based pruning (e.g., {'timestamp': {'$lt': ...}}).

        Args:
            where: Metadata filter to match documents for deletion

        Returns:
            Number of documents deleted
        """
        pass


class GraphStoreAdapter(ABC):
    """
    Protocol for relationship graph storage.

    Handles entities, concepts, and their relationships for
    structured knowledge representation.

    Implementations might use: NetworkX, Neo4j, ElementX, etc.
    """

    # --- CRUD Operations ---

    @abstractmethod
    async def add_node(self, node: "GraphNode") -> bool:
        """
        Adds a node to the graph.

        The node must include provenance metadata (enforced by Pydantic).

        Args:
            node: The GraphNode to add

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def add_edge(self, edge: "GraphEdge") -> bool:
        """
        Adds an edge (relationship) between two nodes.

        The edge must include provenance metadata.

        Args:
            edge: The GraphEdge to add

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def remove_node(self, node_id: str) -> bool:
        """
        Removes a node and all its connected edges.

        Args:
            node_id: The ID of the node to remove

        Returns:
            True if successful, False otherwise
        """
        pass

    # --- Traversal Operations ---

    @abstractmethod
    async def get_neighbors(self, node_id: str, depth: int = 1) -> list[dict[str, Any]]:
        """
        Gets connected nodes within the specified depth.

        Args:
            node_id: The starting node ID
            depth: How many hops to traverse (default 1 = immediate neighbors)

        Returns:
            List of neighbor node dicts with relationship info
        """
        pass

    @abstractmethod
    async def find_path(
        self, start_id: str, end_id: str, max_depth: int = 5
    ) -> list[str]:
        """
        Finds a path between two nodes.

        Args:
            start_id: Starting node ID
            end_id: Target node ID
            max_depth: Maximum path length to search

        Returns:
            List of node IDs representing the path, or empty list if no path
        """
        pass

    # --- Maintenance & Intelligence Operations ---

    @abstractmethod
    async def merge_nodes(self, primary_id: str, secondary_id: str) -> bool:
        """
        Entity Resolution: Merges two nodes representing the same entity.

        Algorithm:
        1. Identify all edges where secondary is source/target
        2. Create copies of those edges pointing to/from primary
        3. Copy unique properties from secondary to primary (primary wins conflicts)
        4. Delete secondary node
        5. Emit 'graph_node_merged' telemetry event

        Used when the Agent realizes 'Bob' and 'Robert' are the same person.

        Args:
            primary_id: The node to keep
            secondary_id: The node to merge into primary and delete

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def fuzzy_search(
        self, query: str, threshold: float = 0.8
    ) -> list["GraphNode"]:
        """
        Finds nodes with similar names/labels.

        Used to prevent duplicate entity creation (e.g., 'Bob' vs 'Robert').

        Args:
            query: The search string
            threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            List of matching GraphNodes
        """
        pass

    @abstractmethod
    async def rank_nodes(self, algorithm: str = "pagerank") -> list[dict[str, Any]]:
        """
        Ranks nodes by importance using graph algorithms.

        Args:
            algorithm: The ranking algorithm to use (default: "pagerank")

        Returns:
            List of dicts with node_id and rank score, sorted by rank
        """
        pass

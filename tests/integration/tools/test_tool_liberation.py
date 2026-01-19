import pytest
import shutil
from pathlib import Path

from friday_memory import MemoryController, ElementXGraphStore, ChromaVectorStore
from friday_core import TranscriptBackedEpisodicStore
from friday_memory.models import GraphNode, GraphEdge, ProvenanceMetadata
from friday_memory.maintenance import MemoryReorganizer
from friday_llm import LiteLLMService, LiteLLMEmbeddingService
from friday_tools.memory.inspection import GraphInspectionTool
from friday_tools.memory.maintenance import MemoryMaintenanceTool

# We need a mock LLM for the Reorganizer/Controller to not fail on init,
# even if we don't call it for these specific tests.
class MockLLM(LiteLLMService):
    def __init__(self):
        pass

class MockEmbedding(LiteLLMEmbeddingService):
    def __init__(self):
        pass
    async def embed_query(self, text):
        return [0.1] * 1536
    async def embed_documents(self, texts):
        return [[0.1] * 1536 for _ in texts]

@pytest.fixture
def test_dir(tmp_path):
    d = tmp_path / "friday_tool_test"
    d.mkdir()
    yield d
    shutil.rmtree(d)

@pytest.fixture
def memory_controller(test_dir):
    # Setup Stores
    graph = ElementXGraphStore(storage_path=str(test_dir / "graph.json"))
    vector = ChromaVectorStore(
        collection_name="tool_test",
        embedding_function=MockEmbedding(),
        persist_directory=str(test_dir / "vector")
    )
    # Mock transcript store for episodic
    episodic = TranscriptBackedEpisodicStore(
        transcript_store=None,  # Not needed for these tests
        model_name="mock",
        system_prompt="mock"
    )
    # Patch episodic to not crash without store
    episodic.get_turns = lambda *a, **k: []
    
    return MemoryController(
        graph_store=graph,
        vector_store=vector,
        episodic_store=episodic
    )

@pytest.mark.asyncio
async def test_tools_integration(memory_controller, test_dir):
    # 1. Setup Data
    prov = ProvenanceMetadata(source_id="turn1", source_type="turn", confidence=1.0)
    node = GraphNode(id="node1", type="Person", label="Alice", provenance=prov)
    await memory_controller.graph.add_node(node)
    
    edge = GraphEdge(source_id="node1", target_id="node2", relation="knows", provenance=prov)
    await memory_controller.graph.add_edge(edge)
    
    # 2. Test Inspection Tool
    inspect_tool = GraphInspectionTool(memory_controller)
    result = await inspect_tool.run(GraphInspectionTool.Input(limit=10))
    
    assert "Alice" in result.content
    assert result.metadata["node_count"] >= 1
    
    # 3. Test Maintenance Tool (Prune Dry Run)
    reorganizer = MemoryReorganizer(
        memory_dir=test_dir,
        config=None,
        llm_service=MockLLM(),
        embedding_function=MockEmbedding(),
        collection_name="tool_test",
        graph_store=memory_controller.graph # Inject graph store
    )
    
    maintain_tool = MemoryMaintenanceTool(reorganizer)
    
    # We expect this to run without crashing, even if it doesn't prune anything useful
    # because we mocked the LLM.
    try:
        result = await maintain_tool.run(
            MemoryMaintenanceTool.Input(operation="prune", dry_run=True)
        )
        assert result.metadata["operation"] == "prune"
        assert result.metadata["dry_run"] is True
    except Exception as e:
        pytest.fail(f"Maintenance tool failed: {e}")

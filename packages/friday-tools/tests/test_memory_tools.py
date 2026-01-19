import pytest
from unittest.mock import AsyncMock, MagicMock
from pydantic import BaseModel

from friday_tools.memory.inspection import MemoryStatsTool, GraphInspectionTool, VectorInspectionTool
from friday_memory import MemoryController, SessionState

# Mock Models
class MockNode(BaseModel):
    id: str = "node1"
    label: str = "Test Node"
    type: str = "Entity"
    hit_count: int = 1

class MockEdge(BaseModel):
    source_id: str = "node1"
    target_id: str = "node2"
    relation: str = "related_to"


@pytest.fixture
def mock_controller():
    controller = MagicMock(spec=MemoryController)
    controller.graph = AsyncMock()
    controller.vector = AsyncMock()
    
    # Setup graph returns
    controller.graph.get_all_nodes.return_value = [MockNode()]
    controller.graph.get_all_edges.return_value = [MockEdge()]
    
    # Setup vector returns
    controller.vector.get_all.return_value = [
        {"text": "A fact", "metadata": {"type": "insight"}}
    ]
    controller.vector.search.return_value = [
        {"text": "Found fact", "metadata": {"type": "insight"}, "distance": 0.1}
    ]
    # Add episodic mock
    controller.episodic = AsyncMock()
    return controller


@pytest.fixture
def mock_session_state():
    state = MagicMock(spec=SessionState)
    state.turn_count = 5
    state.scoped_vars = {"user": "test"}
    return state


@pytest.mark.asyncio
async def test_memory_stats_tool(mock_controller, mock_session_state):
    tool = MemoryStatsTool(mock_controller, mock_session_state)
    
    result = await tool.run(MemoryStatsTool.Input(session_id="sess_123"))
    
    assert "Turns in session: 5" in result.content
    assert result.data["variable_count"] == 1


@pytest.mark.asyncio
async def test_graph_inspection_tool(mock_controller):
    tool = GraphInspectionTool(mock_controller)
    
    result = await tool.run(GraphInspectionTool.Input(limit=10))
    
    assert "Test Node" in result.content
    assert len(result.data["nodes"]) == 1
    assert result.data["edges"][0]["relation"] == "related_to"


@pytest.mark.asyncio
async def test_vector_inspection_tool_get_all(mock_controller):
    tool = VectorInspectionTool(mock_controller)
    
    result = await tool.run(VectorInspectionTool.Input(limit=10, doc_type="insight"))
    
    mock_controller.vector.get_all.assert_called_with(limit=10, where={"type": "insight"})
    assert "A fact" in result.content


@pytest.mark.asyncio
async def test_vector_inspection_tool_search(mock_controller):
    tool = VectorInspectionTool(mock_controller)
    
    result = await tool.run(VectorInspectionTool.Input(
        limit=5, 
        doc_type="all", 
        query="something"
    ))
    
    mock_controller.vector.search.assert_called_with(
        query="something", 
        limit=5, 
        where={}
    )
    assert "Found fact" in result.content

# --- Maintenance Tool Tests ---

from friday_tools.memory.maintenance import MemoryMaintenanceTool, MemoryResetTool
from friday_memory.maintenance import MemoryReorganizer

@pytest.fixture
def mock_reorganizer():
    reorg = MagicMock(spec=MemoryReorganizer)
    reorg.backup = AsyncMock()
    
    # Create a mock report object that has a .dict() method
    report_mock = MagicMock()
    report_mock.dict.return_value = {"entities_removed": 5}
    report_mock.model_dump.return_value = {"entities_removed": 5}
    # Also support attribute access
    report_mock.entities_removed = 5
    
    reorg.prune = AsyncMock(return_value=report_mock)
    reorg.reorganize = AsyncMock(return_value=report_mock)
    return reorg


@pytest.mark.asyncio
async def test_maintenance_tool_prune(mock_reorganizer):
    tool = MemoryMaintenanceTool(mock_reorganizer)
    
    # Run Prune (dry run)
    result = await tool.run(MemoryMaintenanceTool.Input(operation="prune", dry_run=True))
    
    mock_reorganizer.prune.assert_called_with(dry_run=True, backup_first=False)
    assert result.data["entities_removed"] == 5
    # Verify backup was NOT called (default backup_first=True, but we didn't check dry_run logic here?)
    # Wait, code says: if not args.dry_run and args.backup_first: await backup()
    mock_reorganizer.backup.assert_not_called()


@pytest.mark.asyncio
async def test_maintenance_tool_execute_backup(mock_reorganizer):
    tool = MemoryMaintenanceTool(mock_reorganizer)
    
    # Run Prune (EXECUTE)
    await tool.run(MemoryMaintenanceTool.Input(operation="prune", dry_run=False, backup_first=True))
    
    # Should backup first
    mock_reorganizer.backup.assert_called_once()
    mock_reorganizer.prune.assert_called_with(dry_run=False, backup_first=False)


@pytest.mark.asyncio
async def test_reset_tool(mock_controller):
    tool = MemoryResetTool(mock_controller)
    
    # Run Reset
    await tool.run(MemoryResetTool.Input(confirm=True, session_id="sess_1"))
    
    mock_controller.graph.clear.assert_called_once()
    mock_controller.vector.clear.assert_called_once()
    mock_controller.episodic.clear_session.assert_called_with("sess_1")

# --- Lifecycle Tool Tests ---

from friday_tools.memory.lifecycle import LifecycleTool
from friday_memory import MemoryPromotionService

@pytest.fixture
def mock_promotion_service():
    service = MagicMock(spec=MemoryPromotionService)
    service.collection_manager = MagicMock()
    service.collection_manager.get_stats = AsyncMock(return_value={"short": 1, "long": 2})
    
    cycle_res = MagicMock()
    cycle_res.promoted_to_long_term = 5
    cycle_res.decayed_from_long_term = 0
    cycle_res.reactivated = 0
    cycle_res.errors = []
    
    service.run_promotion_cycle = AsyncMock(return_value=cycle_res)
    return service

@pytest.mark.asyncio
async def test_lifecycle_tool(mock_promotion_service):
    tool = LifecycleTool(mock_promotion_service)
    
    # Test Stats
    res1 = await tool.run(LifecycleTool.Input(action="stats"))
    assert res1.data["short"] == 1
    
    # Test Cycle
    res2 = await tool.run(LifecycleTool.Input(action="run_cycle", dry_run=True))
    assert res2.data["promoted"] == 5
    mock_promotion_service.run_promotion_cycle.assert_called_with(dry_run=True)


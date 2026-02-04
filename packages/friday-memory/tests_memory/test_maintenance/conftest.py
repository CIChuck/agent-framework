"""
Test fixtures for maintenance utilities.

Creates memory stores with known issues for testing:
- Orphaned edges
- Duplicate entities
- Stale entities
- Cross-store inconsistencies
"""

import json
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest


@pytest.fixture
def temp_memory_dir():
    """Create a temporary memory directory."""
    temp_dir = tempfile.mkdtemp(prefix="friday_memory_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def memory_with_issues(temp_memory_dir):
    """
    Create a memory directory with planted issues for testing.

    Issues:
    - 2 orphaned edges (pointing to non-existent nodes)
    - 2 duplicate entity groups (exact match, fuzzy match)
    - 3 stale entities (old, low hit_count)
    - 1 cross-store mismatch (insight references missing entity)
    """
    memory_dir = temp_memory_dir
    vector_dir = memory_dir / "vector"
    vector_dir.mkdir(parents=True)

    # Create graph.json with issues
    now = datetime.now()
    old_date = (now - timedelta(days=120)).isoformat()
    recent_date = now.isoformat()

    graph_data = {
        "nodes": {
            # Normal nodes
            "python": {
                "label": "Python",
                "type": "technology",
                "hit_count": 10,
                "last_accessed": recent_date,
                "provenance": {
                    "source_id": "turn_001",
                    "source_type": "interaction",
                    "confidence": 0.9,
                    "created_at": recent_date,
                },
            },
            "javascript": {
                "label": "JavaScript",
                "type": "technology",
                "hit_count": 8,
                "last_accessed": recent_date,
                "provenance": {
                    "source_id": "turn_002",
                    "source_type": "interaction",
                    "confidence": 0.85,
                    "created_at": recent_date,
                },
            },
            # Duplicate entities (exact match - case difference)
            "chuck": {
                "label": "Chuck",
                "type": "person",
                "hit_count": 15,
                "last_accessed": recent_date,
                "provenance": {
                    "source_id": "turn_001",
                    "source_type": "interaction",
                    "confidence": 0.95,
                    "created_at": recent_date,
                },
            },
            "chuck_2": {
                "label": "chuck",  # Same label, different case
                "type": "person",
                "hit_count": 3,
                "last_accessed": recent_date,
                "provenance": {
                    "source_id": "turn_003",
                    "source_type": "interaction",
                    "confidence": 0.8,
                    "created_at": recent_date,
                },
            },
            # Fuzzy duplicates
            "friday_ai": {
                "label": "Friday AI",
                "type": "project",
                "hit_count": 20,
                "last_accessed": recent_date,
                "provenance": {
                    "source_id": "turn_001",
                    "source_type": "interaction",
                    "confidence": 0.9,
                    "created_at": recent_date,
                },
            },
            "friday_assistant": {
                "label": "Friday Assistant",  # Fuzzy match
                "type": "project",
                "hit_count": 5,
                "last_accessed": recent_date,
                "provenance": {
                    "source_id": "turn_004",
                    "source_type": "interaction",
                    "confidence": 0.7,
                    "created_at": recent_date,
                },
            },
            # Stale entities
            "old_project": {
                "label": "Old Project",
                "type": "project",
                "hit_count": 0,
                "last_accessed": old_date,
                "provenance": {
                    "source_id": "turn_old",
                    "source_type": "interaction",
                    "confidence": 0.5,
                    "created_at": old_date,
                },
            },
            "forgotten_tech": {
                "label": "Forgotten Tech",
                "type": "technology",
                "hit_count": 0,
                "last_accessed": old_date,
                "provenance": {
                    "source_id": "turn_old",
                    "source_type": "interaction",
                    "confidence": 0.4,
                    "created_at": old_date,
                },
            },
            "rarely_used": {
                "label": "Rarely Used",
                "type": "concept",
                "hit_count": 0,
                "last_accessed": old_date,
                "provenance": {
                    "source_id": "turn_old",
                    "source_type": "interaction",
                    "confidence": 0.3,
                    "created_at": old_date,
                },
            },
        },
        "edges": [
            # Normal edges
            {
                "source": "chuck",
                "target": "python",
                "relation": "USES",
                "provenance": {
                    "source_id": "turn_001",
                    "source_type": "interaction",
                    "confidence": 0.9,
                    "created_at": recent_date,
                },
            },
            {
                "source": "chuck",
                "target": "friday_ai",
                "relation": "CREATED",
                "provenance": {
                    "source_id": "turn_001",
                    "source_type": "interaction",
                    "confidence": 0.95,
                    "created_at": recent_date,
                },
            },
            # Orphaned edges (target doesn't exist)
            {
                "source": "chuck",
                "target": "nonexistent_node_1",
                "relation": "KNOWS",
                "provenance": {
                    "source_id": "turn_005",
                    "source_type": "interaction",
                    "confidence": 0.5,
                    "created_at": recent_date,
                },
            },
            # Orphaned edge (source doesn't exist)
            {
                "source": "deleted_user",
                "target": "python",
                "relation": "USES",
                "provenance": {
                    "source_id": "turn_006",
                    "source_type": "interaction",
                    "confidence": 0.5,
                    "created_at": recent_date,
                },
            },
        ],
    }

    graph_path = memory_dir / "graph.json"
    graph_path.write_text(json.dumps(graph_data, indent=2))

    # Create transcript.db with turns
    transcript_path = vector_dir / "transcript.db"
    conn = sqlite3.connect(transcript_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS turns (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            user_message TEXT,
            assistant_message TEXT,
            timestamp TEXT,
            consolidated INTEGER DEFAULT 0
        )
    """)

    # Add some turns (but not all referenced in provenance)
    turns = [
        ("turn_001", "session_1", "Hello", "Hi there!", recent_date, 1),
        ("turn_002", "session_1", "What is Python?", "Python is...", recent_date, 1),
        ("turn_003", "session_1", "Tell me about Chuck", "Chuck is...", recent_date, 0),
        # turn_004, turn_005, turn_006, turn_old are missing - will cause orphaned provenance
    ]

    conn.executemany(
        "INSERT INTO turns VALUES (?, ?, ?, ?, ?, ?)",
        turns
    )
    conn.commit()
    conn.close()

    # Note: ChromaDB fixtures would require actual chromadb setup
    # For basic testing, we just have the graph and transcript

    return memory_dir


@pytest.fixture
def clean_memory_dir(temp_memory_dir):
    """Create a clean memory directory with valid data (no issues)."""
    memory_dir = temp_memory_dir
    vector_dir = memory_dir / "vector"
    vector_dir.mkdir(parents=True)

    now = datetime.now().isoformat()

    graph_data = {
        "nodes": {
            "python": {
                "label": "Python",
                "type": "technology",
                "hit_count": 10,
                "last_accessed": now,
                "provenance": {
                    "source_id": "turn_001",
                    "source_type": "interaction",
                    "confidence": 0.9,
                    "created_at": now,
                },
            },
            "chuck": {
                "label": "Chuck",
                "type": "person",
                "hit_count": 15,
                "last_accessed": now,
                "provenance": {
                    "source_id": "turn_001",
                    "source_type": "interaction",
                    "confidence": 0.95,
                    "created_at": now,
                },
            },
        },
        "edges": [
            {
                "source": "chuck",
                "target": "python",
                "relation": "USES",
                "provenance": {
                    "source_id": "turn_001",
                    "source_type": "interaction",
                    "confidence": 0.9,
                    "created_at": now,
                },
            },
        ],
    }

    graph_path = memory_dir / "graph.json"
    graph_path.write_text(json.dumps(graph_data, indent=2))

    # Create transcript.db
    transcript_path = vector_dir / "transcript.db"
    conn = sqlite3.connect(transcript_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS turns (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            user_message TEXT,
            assistant_message TEXT,
            timestamp TEXT,
            consolidated INTEGER DEFAULT 0
        )
    """)

    conn.execute(
        "INSERT INTO turns VALUES (?, ?, ?, ?, ?, ?)",
        ("turn_001", "session_1", "Hello", "Hi!", now, 1)
    )
    conn.commit()
    conn.close()

    return memory_dir

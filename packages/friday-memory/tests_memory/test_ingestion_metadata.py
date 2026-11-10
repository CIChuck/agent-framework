"""Absent optional ingestion fields must never become invalid store metadata."""

import os
import subprocess
import sys

import pytest
from friday_memory.ingestion.metadata import build_ingested_file_metadata


@pytest.mark.parametrize("description", [None, "", "project notes"])
def test_ingestion_description_presence_is_preserved(description):
    metadata = build_ingested_file_metadata("fixture.txt", description)
    expected = {"source": "fixture.txt", "type": "ingested_file"}
    if description is not None:
        expected["description"] = description
    assert metadata == expected
    assert all(isinstance(value, str) for value in metadata.values())
    metadata["source"] = "changed"
    assert build_ingested_file_metadata("fixture.txt", description) == expected


def test_ingestion_metadata_has_no_frontend_dependency(tmp_path):
    code = """
import sys
class NoFrontends:
    def find_spec(self, fullname, *_args):
        if fullname.split('.')[0] in {'friday_chat', 'friday_commands', 'friday_tui'}:
            raise RuntimeError('frontend dependency: ' + fullname)
sys.meta_path.insert(0, NoFrontends())
from friday_memory.ingestion.metadata import build_ingested_file_metadata
if build_ingested_file_metadata('fixture.txt', None) != {'source':'fixture.txt','type':'ingested_file'}:
    raise RuntimeError('invalid shared metadata')
print('headless ingestion metadata passed')
"""
    run = subprocess.run(
        [sys.executable, "-I", "-B", "-c", code],
        cwd=tmp_path,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "headless ingestion metadata passed" in run.stdout

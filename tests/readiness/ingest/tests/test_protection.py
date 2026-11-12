from __future__ import annotations

import os
import unittest

from ingest.manifests import Refusal
from ingest.protection import snapshot, unchanged
from ingest.startup import Guard, guarded
from ingest.tests.test_manifests import unit


class Protection(unittest.TestCase):
    def test_intercepted_reads_stat_and_writes_refuse_before_effect(self) -> None:
        owned, outside = unit(), unit()
        target = outside / "sentinel"
        target.write_text("fake private control")
        with guarded(Guard((owned,), (owned,))):
            (owned / "positive").write_text("ok")
            for action in (
                lambda: target.read_text(),
                lambda: os.stat(target),
                lambda: (outside / "created").write_text("bad"),
            ):
                with self.assertRaises(Refusal):
                    action()
        self.assertFalse((outside / "created").exists())
        self.assertEqual((owned / "positive").read_text(), "ok")

    def test_native_like_change_is_detected_not_called_prevented(self) -> None:
        root = unit()
        before = snapshot((root,), 20)
        (root / "fake-native-cache-write").write_text("changed")
        with self.assertRaises(Refusal):
            unchanged(before, snapshot((root,), 20))
        self.assertTrue((root / "fake-native-cache-write").exists())

    def test_missing_root_and_truncated_coverage(self) -> None:
        root = unit()
        absent = root / "absent"
        before = snapshot((absent,), 2)
        unchanged(before, snapshot((absent,), 2))
        for index in range(3):
            (root / str(index)).write_bytes(b"")
        with self.assertRaises(Refusal):
            snapshot((root,), 2)

    def test_dir_fd_threads_and_sockets_refuse_before_effect(self) -> None:
        import _thread
        import socket

        owned, other = unit(), unit()
        fd = os.open(other, os.O_RDONLY)
        try:
            with guarded(Guard((owned,), (owned,))):
                with self.assertRaises(Refusal):
                    os.open("escape", os.O_CREAT | os.O_WRONLY, dir_fd=fd)
                with self.assertRaises(Refusal):
                    _thread.start_new_thread(lambda: None, ())
                with self.assertRaises(Refusal):
                    socket.socket()
                with self.assertRaises(Refusal):
                    owned.parent.read_bytes()
                os.stat(owned.parent)  # Canonicalization metadata only, never payloads.
        finally:
            os.close(fd)
        self.assertFalse((other / "escape").exists())

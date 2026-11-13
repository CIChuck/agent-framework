from __future__ import annotations

import os
import stat
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

    def test_standard_and_saved_low_level_thread_launches_refuse(self) -> None:
        import _thread
        import threading

        from ingest.startup import _original_thread

        # Bind before the nested guard, including the unwrapped builtin captured
        # before installation. The audit boundary must cover all these aliases.
        thread_class = threading.Thread
        low_level = (
            _original_thread,
            _thread.start_new,
            _thread.start_new_thread,
        )
        joinable = _thread.start_joinable_thread
        owned, outside = unit(), unit()
        marker = outside / "thread-effect"
        finished = threading.Event()

        def worker() -> None:
            try:
                marker.write_text("unexpected worker")
            finally:
                finished.set()

        def standard() -> None:
            thread = thread_class(target=worker)
            thread.start()
            thread.join(timeout=2)

        with guarded(Guard((owned,), (owned,))):
            with self.assertRaisesRegex(Refusal, "worker thread"):
                standard()
            for start in low_level:
                with (
                    self.subTest(start=start),
                    self.assertRaisesRegex(Refusal, "worker thread"),
                ):
                    start(worker, ())
                    finished.wait(2)
            with self.assertRaisesRegex(Refusal, "worker thread"):
                joinable(worker)
                finished.wait(2)
            (owned / "positive").write_text("still guarded")
        self.assertFalse(marker.exists())
        self.assertFalse(finished.is_set())
        self.assertEqual((owned / "positive").read_text(), "still guarded")

    def test_all_qualified_dir_fd_mutations_refuse_and_preserve_targets(self) -> None:
        owned, outside = unit(), unit()
        target = outside / "sentinel"
        target.write_bytes(b"unchanged private payload")
        os.chmod(target, 0o644)
        os.utime(target, ns=(1_000_000_000, 2_000_000_000))
        (outside / "directory").mkdir()
        fd = os.open(outside, os.O_RDONLY)
        before = target.stat()
        actions = {
            "open": lambda: os.open("created", os.O_CREAT | os.O_WRONLY, dir_fd=fd),
            "mkdir": lambda: os.mkdir("created", dir_fd=fd),
            "remove": lambda: os.remove("sentinel", dir_fd=fd),
            "unlink": lambda: os.unlink("sentinel", dir_fd=fd),
            "rmdir": lambda: os.rmdir("directory", dir_fd=fd),
            "chmod": lambda: os.chmod("sentinel", 0o600, dir_fd=fd),
            "utime": lambda: os.utime("sentinel", ns=(3, 4), dir_fd=fd),
            "chown": lambda: os.chown("sentinel", -1, -1, dir_fd=fd),
            "rename_source": lambda: os.rename(
                "sentinel", owned / "created", src_dir_fd=fd
            ),
            "rename_destination": lambda: os.rename(
                owned / "source", "created", dst_dir_fd=fd
            ),
            "replace": lambda: os.replace(
                "sentinel", "created", src_dir_fd=fd, dst_dir_fd=fd
            ),
            "link_source": lambda: os.link(
                "sentinel", owned / "created", src_dir_fd=fd
            ),
            "link_destination": lambda: os.link(
                owned / "source", "created", dst_dir_fd=fd
            ),
            "symlink": lambda: os.symlink("sentinel", "created", dir_fd=fd),
            "mkfifo": lambda: os.mkfifo("created", dir_fd=fd),
            "mknod": lambda: os.mknod("created", stat.S_IFIFO | 0o600, dir_fd=fd),
        }
        try:
            with guarded(Guard((owned,), (owned,))):
                for name, action in actions.items():
                    with (
                        self.subTest(api=name),
                        self.assertRaisesRegex(Refusal, "dir_fd"),
                    ):
                        action()
                # An absolute spelling does not make an unsupported dir_fd form
                # supported, even though the OS would ignore its directory fd.
                positive = owned / "positive"
                positive.write_text("ok")
                for action in (
                    lambda: os.chmod(positive, 0o600, dir_fd=fd),
                    lambda: os.utime(positive, ns=(3, 4), dir_fd=fd),
                ):
                    with self.assertRaisesRegex(Refusal, "dir_fd"):
                        action()
                os.chmod(positive, 0o640)
                os.utime(positive, ns=(5, 6))
                self.assertEqual(stat.S_IMODE(positive.stat().st_mode), 0o640)
                self.assertEqual(positive.stat().st_mtime_ns, 6)
                os.chown(positive, -1, -1)
                os.mkfifo(owned / "positive-fifo")
                os.mknod(owned / "positive-node", stat.S_IFIFO | 0o600)
        finally:
            os.close(fd)
        after = target.stat()
        self.assertEqual(
            (before.st_mode, before.st_atime_ns, before.st_mtime_ns),
            (after.st_mode, after.st_atime_ns, after.st_mtime_ns),
        )
        self.assertEqual(target.read_bytes(), b"unchanged private payload")
        self.assertEqual(
            sorted(p.name for p in outside.iterdir()), ["directory", "sentinel"]
        )

    def test_descriptor_mutations_and_discovery_refuse_unclassified_targets(
        self,
    ) -> None:
        owned, outside = unit(), unit()
        target = outside / "sentinel"
        target.write_text("unchanged")
        fd = os.open(target, os.O_RDWR)
        directory_fd = os.open(outside, os.O_RDONLY)
        before = target.stat()
        try:
            with guarded(Guard((owned,), (owned,))):
                for action in (
                    lambda: os.fchmod(fd, 0o600),
                    lambda: os.fchown(fd, -1, -1),
                    lambda: os.ftruncate(fd, 0),
                    lambda: os.utime(fd, ns=(1, 2)),
                    lambda: os.stat(fd),
                    lambda: os.fstat(fd),
                    lambda: os.listdir(directory_fd),
                    lambda: os.scandir(directory_fd),
                    lambda: os.fchdir(directory_fd),
                ):
                    with (
                        self.subTest(action=action),
                        self.assertRaisesRegex(
                            Refusal, "Unclassified regular file descriptor"
                        ),
                    ):
                        action()
        finally:
            os.close(fd)
            os.close(directory_fd)
        after = target.stat()
        self.assertEqual(
            (before.st_mode, before.st_atime_ns, before.st_mtime_ns, before.st_size),
            (after.st_mode, after.st_atime_ns, after.st_mtime_ns, after.st_size),
        )
        self.assertEqual(target.read_text(), "unchanged")

    def test_access_and_supported_discovery_refuse_present_absent_and_dir_fd(
        self,
    ) -> None:
        owned, outside = unit(), unit()
        present, absent = outside / "sentinel", outside / "absent"
        present.write_text("fake private control")
        (owned / "positive").write_text("ok")
        fd = os.open(outside, os.O_RDONLY)
        try:
            with guarded(Guard((owned,), (owned,))):
                self.assertTrue(os.access(owned / "positive", os.F_OK))
                self.assertFalse(os.access(owned / "missing", os.F_OK))
                for path in (present, absent, owned.parent):
                    for mode in (os.F_OK, os.R_OK):
                        with (
                            self.subTest(path=path, mode=mode),
                            self.assertRaisesRegex(Refusal, "Undeclared read/probe"),
                        ):
                            os.access(path, mode)
                for action in (
                    lambda: os.access("sentinel", os.F_OK, dir_fd=fd),
                    lambda: os.access("absent", os.F_OK, dir_fd=fd),
                    lambda: os.stat("sentinel", dir_fd=fd),
                    lambda: os.lstat("sentinel", dir_fd=fd),
                    lambda: os.readlink("sentinel", dir_fd=fd),
                ):
                    with self.assertRaisesRegex(Refusal, "dir_fd"):
                        action()
                for path in (present, absent):
                    for probe in (os.stat, os.lstat, os.readlink):
                        with (
                            self.subTest(path=path),
                            self.assertRaisesRegex(Refusal, "Undeclared read/probe"),
                        ):
                            probe(path)
                    # These stdlib convenience functions catch ValueError from
                    # the intercepted stat/lstat and conservatively return False.
                    self.assertFalse(path.exists())
                    self.assertFalse(path.is_file())
                    self.assertFalse(os.path.exists(path))
                    self.assertFalse(os.path.lexists(path))
                for listing in (
                    lambda: os.listdir(outside),
                    lambda: os.scandir(outside),
                ):
                    with self.assertRaisesRegex(Refusal, "Undeclared read/probe"):
                        listing()
                # Ancestor stat metadata remains available for physical() checks,
                # but never grants access/listing/payload permission on ancestors.
                os.stat(owned.parent)
                self.assertEqual(os.listdir(owned), ["positive"])
        finally:
            os.close(fd)

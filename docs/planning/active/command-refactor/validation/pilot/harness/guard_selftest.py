"""Exercise the injected guard without calling providers or opening real stores."""

from __future__ import annotations

import os
import socket
import sqlite3
import subprocess
import sys
from pathlib import Path


def main() -> None:
    attempts = {
        "dns": lambda: socket.getaddrinfo("pilot.invalid", 443),
        "store": lambda: (Path.home() / ".friday/pilot-guard-probe").read_text(),
        "repo_store": lambda: (
            Path(os.environ["REVIEW_REPO"]) / ".friday/pilot-probe"
        ).read_text(),
        "sqlite_home_audit": lambda: sys.audit(
            "sqlite3.connect", str(Path.home() / ".friday/probe.db")
        ),
        "sqlite_repo_audit": lambda: sys.audit(
            "sqlite3.connect", str(Path(os.environ["REVIEW_REPO"]) / ".friday/probe.db")
        ),
    }
    if sys.platform == "darwin":
        attempts.update(
            {
                "sqlite_home_case": lambda: sys.audit(
                    "sqlite3.connect", str(Path.home() / ".FRIDAY/probe.db")
                ),
                "sqlite_repo_case": lambda: sys.audit(
                    "sqlite3.connect",
                    str(Path(os.environ["REVIEW_REPO"]) / ".Friday/probe.db"),
                ),
                "open_home_case": lambda: sys.audit(
                    "open", str(Path.home() / ".FRIDAY/probe.db"), "r", 0
                ),
            }
        )
    with (
        socket.socket() as connection,
        socket.socket(type=socket.SOCK_DGRAM) as datagram,
    ):
        attempts.update(
            {
                "connect": lambda: connection.connect(("203.0.113.1", 443)),
                "connect_ex": lambda: connection.connect_ex(("203.0.113.1", 443)),
                "sendto": lambda: datagram.sendto(b"probe", ("203.0.113.1", 443)),
                "nonlocal_bind": lambda: datagram.bind(("0.0.0.0", 0)),
            }
        )
        for name, operation in attempts.items():
            try:
                operation()
            except RuntimeError as error:
                if "guard blocked" not in str(error):
                    raise
            else:
                raise RuntimeError(f"Guard failed its refusal control: {name}")
    with socket.socket() as server, socket.socket() as client:
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        client.connect(server.getsockname())
        accepted, _ = server.accept()
        accepted.close()
    # Actual SQLite refusal probes use a synthetic repo under scratch. A broken
    # guard can create only our disposable fixture, never a real user database.
    fake = Path(os.environ["REVIEW_SCRATCH"]) / "sqlite-guard-fixture"
    (fake / ".friday").mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, REVIEW_REPO=str(fake))
    database = fake / ".friday/probe.db"
    sqlite_values = [
        str(database),
        "file:" + str(database),
        "file:" + str(database).replace(".friday", "%2Efriday"),
    ]
    if sys.platform == "darwin":
        sqlite_values.append(str(database).replace(".friday", ".FRIDAY"))
    for value in sqlite_values:
        code = (
            "import sqlite3,sys\n"
            "try: sqlite3.connect(sys.argv[1], uri=True)\n"
            "except RuntimeError as error:\n"
            " if 'guard blocked' not in str(error): raise\n"
            "else: raise RuntimeError('SQLite protection failed')\n"
        )
        subprocess.run(
            [sys.executable, "-B", "-c", code, value], env=environment, check=True
        )
        if database.exists():
            raise RuntimeError("SQLite refusal created a protected fixture file")
    for statement in ("ATTACH DATABASE ? AS protected", "VACUUM INTO ?"):
        code = (
            "import sqlite3,sys\nc=sqlite3.connect(':memory:')\n"
            "try: c.execute(sys.argv[1], (sys.argv[2],))\n"
            "except sqlite3.DatabaseError as error:\n"
            " if 'authoriz' not in str(error): raise\n"
            "else: raise RuntimeError('SQLite authorizer protection failed')\n"
        )
        subprocess.run(
            [sys.executable, "-B", "-c", code, statement, str(database)],
            env=environment,
            check=True,
        )
        if database.exists():
            raise RuntimeError(
                "SQL authorizer refusal created a protected fixture file"
            )
    with sqlite3.connect(":memory:"):
        pass
    with sqlite3.connect(Path(os.environ["REVIEW_SCRATCH"]) / "allowed-sqlite.db"):
        pass
    print(
        f"Guard passed {len(attempts) + len(sqlite_values) + 2} refusal controls, loopback and scratch/memory SQLite controls"
    )


if __name__ == "__main__":
    main()

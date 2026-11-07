"""Exercise the injected guard without calling providers or opening real stores."""

from __future__ import annotations

import os
import socket
from pathlib import Path


def main() -> None:
    attempts = {
        "dns": lambda: socket.getaddrinfo("pilot.invalid", 443),
        "store": lambda: (Path.home() / ".friday/pilot-guard-probe").read_text(),
        "repo_store": lambda: (
            Path(os.environ["REVIEW_REPO"]) / ".friday/pilot-probe"
        ).read_text(),
    }
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
    print(
        f"Guard passed {len(attempts)} refusal controls and disposable loopback control"
    )


if __name__ == "__main__":
    main()

"""Public identity contract shared by Friday frontends."""

from __future__ import annotations

import pickle
import re
import subprocess
import sys
from dataclasses import FrozenInstanceError

import pytest
from friday_runtime.session_identity import (
    SessionIdentity,
    SessionIdentityMismatchError,
    resolve_session_identity,
)


def test_generated_identity_shape_uniqueness_and_immutability() -> None:
    first = SessionIdentity.generate()
    second = SessionIdentity.generate()

    assert re.fullmatch(r"session_[0-9a-f]{32}", first.value)
    assert first != second
    assert str(first) == first.value
    identity_attribute = "value"
    with pytest.raises(FrozenInstanceError):
        setattr(first, identity_attribute, "replacement")


@pytest.mark.parametrize("value", ["", " ", " leading", "trailing "])
def test_identity_rejects_empty_or_untrimmed_values(value: str) -> None:
    with pytest.raises(ValueError, match="^session identity must be non-empty and trimmed$"):
        SessionIdentity(value)


def test_resolver_reuses_typed_identity_and_validates_string_injection() -> None:
    identity = SessionIdentity("injected-session")

    assert resolve_session_identity(session_identity=identity) is identity
    assert (
        resolve_session_identity(session_identity=identity, session_id=identity.value)
        is identity
    )
    assert resolve_session_identity(session_id=identity.value) == identity
    assert re.fullmatch(r"session_[0-9a-f]{32}", resolve_session_identity().value)
    with pytest.raises(ValueError, match="^session identity must be non-empty and trimmed$"):
        resolve_session_identity(session_id=" invalid ")


def test_resolver_rejects_injected_mismatch_with_existing_error() -> None:
    with pytest.raises(
        SessionIdentityMismatchError,
        match="^typed session identity does not match injected session_id$",
    ):
        resolve_session_identity(
            session_identity=SessionIdentity("typed-session"),
            session_id="different-session",
        )


def test_chat_facade_reexports_the_same_objects_and_legacy_class_path() -> None:
    import friday_chat.session as chat_session

    assert chat_session.SessionIdentity is SessionIdentity
    assert chat_session.SessionIdentityMismatchError is SessionIdentityMismatchError
    assert chat_session.resolve_session_identity is resolve_session_identity
    assert pickle.loads(b"cfriday_chat.session\nSessionIdentity\n.") is SessionIdentity

    identity = SessionIdentity("session-shared")
    session = chat_session.FridaySession(
        session_id=identity.value,
        user_id="user",
        identity=identity,
    )
    assert session.identity is identity
    with pytest.raises(
        SessionIdentityMismatchError,
        match="^FridaySession identity does not match its session_id$",
    ):
        chat_session.FridaySession(
            session_id="different-session", user_id="user", identity=identity
        )


def test_neutral_runtime_import_does_not_load_chat_or_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import friday_runtime, friday_runtime.session_identity, sys; "
            "raise SystemExit(any(name.split('.')[0] in {'friday_chat', 'friday_cli'} "
            "for name in sys.modules))",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr

"""Import smoke tests for the FridayV2 skeleton."""

from importlib.metadata import version

import friday_chat
from friday_chat.app import FridayChatApp
from friday_chat.background import BackgroundTaskManager
from friday_chat.config import FridayChatConfigError
from friday_chat.session import FridaySession


def test_package_version_is_defined() -> None:
    assert friday_chat.__version__ == "0.1.0a1"


def test_runtime_version_matches_distribution_metadata() -> None:
    assert friday_chat.__version__ == version("friday-chat")


def test_app_starts() -> None:
    app = FridayChatApp()

    app.start()

    assert app.started is True


def test_session_defaults() -> None:
    session = FridaySession(session_id="s1", user_id="u1")

    assert session.turn_ids == []


def test_config_error_is_value_error() -> None:
    assert issubclass(FridayChatConfigError, ValueError)


async def test_background_manager_closes() -> None:
    manager = BackgroundTaskManager()

    await manager.close()

    assert manager.closed is True

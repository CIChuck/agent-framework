"""Independent constructor boundaries from the approved runtime-validation table."""

from collections.abc import Callable, Iterator
from dataclasses import FrozenInstanceError, fields
from enum import Enum

import pytest
from friday_commands import (
    CommandArgument,
    CommandError,
    CommandExecution,
    CommandOutcome,
    CommandRequest,
    CommandSpec,
    DispatchResult,
    ExitData,
    HelpData,
    NoData,
    UiEffect,
)

SPEC = CommandSpec("help", "Help", "general", "/help")
ARGUMENT = CommandArgument("topic", "Topic")
ERROR = CommandError("unknown_command", "missing")
OUTCOME = CommandOutcome(data=NoData())


class SpecSubclass(CommandSpec):
    pass


class ArgumentSubclass(CommandArgument):
    pass


class DataSubclass(NoData):
    pass


class ErrorSubclass(CommandError):
    pass


class OutcomeSubclass(CommandOutcome):
    pass


class OtherEffect(Enum):
    CLEAR_SCREEN = "clear_screen"


@pytest.mark.parametrize(
    "factory",
    [
        lambda: CommandArgument(1, "Description"),
        lambda: CommandArgument("name", None),
        lambda: CommandArgument("name", "Description", required=1),
        lambda: CommandArgument("name", "Description", default=False),
        lambda: CommandArgument("name", "Description", choices=(1,)),
        lambda: CommandSpec(1, "Description", "category", "usage"),
        lambda: CommandSpec("name", 1, "category", "usage"),
        lambda: CommandSpec("name", "Description", 1, "usage"),
        lambda: CommandSpec("name", "Description", "category", 1),
        lambda: CommandSpec("name", "Description", "category", "usage", aliases=(1,)),
        lambda: CommandSpec(
            "name", "Description", "category", "usage", arguments=(SPEC,)
        ),
        lambda: CommandSpec(
            "name",
            "Description",
            "category",
            "usage",
            arguments=(ArgumentSubclass("a", "A"),),
        ),
        lambda: CommandSpec("name", "Description", "category", "usage", detail=7),
        lambda: CommandRequest(7, (), SPEC),
        lambda: CommandRequest("help", (7,), SPEC),
        lambda: CommandRequest("help", (), object()),
        lambda: CommandRequest(
            "help", (), SpecSubclass("help", "Help", "general", "/help")
        ),
        lambda: CommandExecution(session_id=1),
        lambda: HelpData((ARGUMENT,)),
        lambda: HelpData((SpecSubclass("help", "Help", "general", "/help"),)),
        lambda: HelpData((SPEC,), focused_name=1),
        lambda: ExitData(requested=0),
        lambda: CommandError(1, "name"),
        lambda: CommandError("failed", 1),
        lambda: CommandError("failed", "name", usage=1),
        lambda: CommandOutcome(data={}),
        lambda: CommandOutcome(data="text"),
        lambda: CommandOutcome(data=True),
        lambda: CommandOutcome(data=DataSubclass()),
        lambda: CommandOutcome(error=object()),
        lambda: CommandOutcome(error=ErrorSubclass("failed", "name")),
        lambda: CommandOutcome(data=NoData(), ui_effects=("clear_screen",)),
        lambda: CommandOutcome(data=NoData(), ui_effects=(OtherEffect.CLEAR_SCREEN,)),
        lambda: DispatchResult(1, OUTCOME),
        lambda: DispatchResult(True, NoData()),
        lambda: DispatchResult(True, OutcomeSubclass(data=NoData())),
        lambda: NoData(unexpected=True),
        lambda: NoData(1),
    ],
)
def test_wrong_field_or_member_types(factory: Callable[[], object]) -> None:
    with pytest.raises(TypeError) as exc:
        factory()
    assert type(exc.value) is TypeError


@pytest.mark.parametrize(
    "factory",
    [
        lambda: CommandRequest("HELP", (), SPEC),
        lambda: CommandRequest("/help", (), SPEC),
        lambda: CommandError("not_a_foundation_code", "name"),
        lambda: CommandOutcome(),
        lambda: CommandOutcome(data=NoData(), error=ERROR),
        lambda: CommandOutcome(error=ERROR, ui_effects=(UiEffect.CLEAR_SCREEN,)),
        lambda: DispatchResult(False, OUTCOME),
        lambda: DispatchResult(True, None),
        lambda: UiEffect("unknown"),
    ],
)
def test_invalid_values_and_relationships(factory: Callable[[], object]) -> None:
    with pytest.raises(ValueError) as exc:
        factory()
    assert type(exc.value) is ValueError


COLLECTIONS = [
    (lambda value: CommandArgument("a", "A", choices=value), "choices", "x"),
    (lambda value: CommandSpec("a", "A", "test", "/a", aliases=value), "aliases", "x"),
    (
        lambda value: CommandSpec("a", "A", "test", "/a", arguments=value),
        "arguments",
        ARGUMENT,
    ),
    (lambda value: CommandRequest("help", value, SPEC), "args", "x"),
    (lambda value: HelpData(value), "commands", SPEC),
    (
        lambda value: CommandOutcome(data=NoData(), ui_effects=value),
        "ui_effects",
        UiEffect.CLEAR_SCREEN,
    ),
]


@pytest.mark.parametrize(("factory", "attribute", "member"), COLLECTIONS)
@pytest.mark.parametrize("invalid", [None, 7, "x", b"x", bytearray(b"x"), {"x": "y"}])
def test_collection_container_rejections(factory, attribute, member, invalid) -> None:
    with pytest.raises(TypeError) as exc:
        factory(invalid)
    assert type(exc.value) is TypeError


@pytest.mark.parametrize(("factory", "attribute", "member"), COLLECTIONS)
def test_snapshot_inputs_once_and_preserve_iterator_exception(
    factory, attribute, member
) -> None:
    supplied = [member]
    result = factory(supplied)
    supplied.clear()
    assert getattr(result, attribute) == (member,)

    class Once:
        def __init__(self) -> None:
            self.calls = 0

        def __iter__(self) -> Iterator[object]:
            self.calls += 1
            if self.calls != 1:
                raise RuntimeError("Iterated twice")
            yield member

    iterable = Once()
    assert getattr(factory(iterable), attribute) == (member,)
    assert iterable.calls == 1

    class Indexed:
        def __getitem__(self, index: int) -> object:
            if index == 0:
                return member
            raise IndexError(index)

    assert getattr(factory(Indexed()), attribute) == (member,)
    failure = RuntimeError("iterator failed")

    def broken() -> Iterator[object]:
        yield member
        raise failure

    with pytest.raises(RuntimeError) as exc:
        factory(broken())
    assert exc.value is failure


def test_valid_defaults_raw_strings_and_closed_variants() -> None:
    class Text(str):
        pass

    argument = CommandArgument(
        Text(" "), Text(" "), False, Text(" raw "), (Text(" A "),)
    )
    spec = CommandSpec(
        Text(" /HELP "), Text(" "), Text(" "), Text(" "), (" ",), (argument,)
    )
    assert spec.name == " /HELP " and spec.aliases == (" ",)
    assert argument.default == " raw " and argument.choices == (" A ",)
    assert CommandExecution().session_id is None
    assert CommandExecution("").session_id == ""
    assert ExitData(False).requested is False
    assert HelpData((SPEC,), " /HELP ").focused_name == " /HELP "
    assert CommandError("unknown_command", "").command_name == ""
    for code in ("unknown_command", "invalid_arguments", "unavailable", "failed"):
        assert CommandError(code, "name").code == code
    for data in (NoData(), HelpData((SPEC,)), ExitData()):
        assert CommandOutcome(data=data).data is data
    assert UiEffect("clear_screen") is UiEffect.CLEAR_SCREEN
    assert CommandOutcome(
        data=ExitData(), ui_effects=(UiEffect.CLEAR_SCREEN,)
    ).ui_effects == (UiEffect.CLEAR_SCREEN,)
    assert DispatchResult(False, None).outcome is None
    assert DispatchResult(True, CommandOutcome(error=ERROR)).outcome.error is ERROR


@pytest.mark.parametrize(
    "model",
    [
        ARGUMENT,
        SPEC,
        CommandRequest("help", (), SPEC),
        CommandExecution(),
        HelpData(()),
        ExitData(),
        ERROR,
        OUTCOME,
        DispatchResult(True, OUTCOME),
    ],
)
def test_model_fields_are_frozen(model: object) -> None:
    name = fields(model)[0].name
    with pytest.raises(FrozenInstanceError):
        setattr(model, name, None)


def test_field_type_validation_precedes_cross_field_invariants() -> None:
    with pytest.raises(TypeError):
        CommandOutcome(data=None, error=None, ui_effects=("clear_screen",))
    with pytest.raises(TypeError):
        DispatchResult(False, "not an outcome")


def test_closed_data_membership_uses_actual_type_identity() -> None:
    class EqualToEveryType(type):
        def __eq__(cls, other: object) -> bool:
            return True

    class ForeignPayload(metaclass=EqualToEveryType):
        pass

    with pytest.raises(TypeError):
        CommandOutcome(data=ForeignPayload())


def test_constructor_collections_preserve_spelling_order_and_duplicates() -> None:
    z = CommandArgument(" Z ", "Z")
    a = CommandArgument(" A ", "A")
    assert CommandArgument("name", "Name", choices=[" Z ", "A", "A"]).choices == (
        " Z ",
        "A",
        "A",
    )
    model = CommandSpec(" RAW ", " D ", " C ", " U ", [" Z ", "A"], [z, a])
    assert model.aliases == (" Z ", "A") and model.arguments == (z, a)
    assert CommandRequest(" RAW ", [" Z ", "A"], model).args == (" Z ", "A")
    second = CommandSpec("a", "A", "test", "/a")
    assert HelpData([model, second]).commands == (model, second)
    assert CommandOutcome(
        data=NoData(), ui_effects=[UiEffect.CLEAR_SCREEN] * 2
    ).ui_effects == (UiEffect.CLEAR_SCREEN, UiEffect.CLEAR_SCREEN)

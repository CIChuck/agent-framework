import asyncio

import pytest
from friday_telemetry import CorrelationScope, ExecutionContext


def test_owner_runtime_validation_and_reset():
    a = CorrelationScope("a" * 16)
    b = CorrelationScope("b" * 16)
    context = a.context(turn=True)
    assert not b.accepts(context)
    with pytest.raises(ValueError), b.bind(context):
        pass
    with pytest.raises(ValueError):
        ExecutionContext("raw", None, object())
    with pytest.raises(RuntimeError), a.bind(context):
        raise RuntimeError("primary")
    assert a.current() is None


@pytest.mark.asyncio
async def test_concurrent_nested_and_expired_inheritance():
    scope = CorrelationScope("a" * 16)
    async def worker():
        context = scope.context(turn=True)
        with scope.bind(context):
            await asyncio.sleep(0)
            assert scope.current().context is context
            with scope.bind(context.child()):
                assert scope.current().context.turn_ref == context.turn_ref
            assert scope.current().context is context
        return context.turn_ref
    assert len(set(await asyncio.gather(worker(), worker()))) == 2
    gate = asyncio.Event()
    async def inherited():
        await gate.wait()
        assert scope.current() is None
    with scope.bind(scope.context(turn=True)):
        task = asyncio.create_task(inherited())
        with scope.clear():
            assert scope.current() is None
        assert scope.current() is not None
    gate.set()
    await task
    assert scope.current() is None


def test_private_delivery_contexts_do_not_change_caller_or_siblings():
    from contextvars import ContextVar
    value = ContextVar("fake_sink_stack", default=())
    value.set(("caller",))
    scope = CorrelationScope("a" * 16)
    with scope.bind(scope.context(turn=True)) as parent:
        parent.delivery_context.run(value.set, ("parent",))
        left = parent.delivery_context.copy()
        right = parent.delivery_context.copy()
        with scope.bind(parent.context.child(), delivery_context=left) as child:
            child.delivery_context.run(value.set, ("parent", "left"))
        assert right.run(value.get) == ("parent",)
        assert parent.delivery_context.run(value.get) == ("parent",)
        assert value.get() == ("caller",)
    assert scope.current() is None

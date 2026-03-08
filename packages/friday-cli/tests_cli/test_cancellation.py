# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""
Tests for cancellation support.
"""

import asyncio

import pytest
from friday_cli.cancellation import (
    CancellableContext,
    CancellationToken,
    OperationCancelledError,
    run_cancellable,
)


class TestCancellationToken:
    """Test CancellationToken class."""

    def test_initial_state(self):
        token = CancellationToken()
        assert not token.is_cancelled

    def test_cancel(self):
        token = CancellationToken()
        token.cancel()
        assert token.is_cancelled

    def test_reset(self):
        token = CancellationToken()
        token.cancel()
        assert token.is_cancelled

        token.reset()
        assert not token.is_cancelled

    @pytest.mark.asyncio
    async def test_wait_for_cancellation(self):
        token = CancellationToken()

        async def cancel_after_delay():
            await asyncio.sleep(0.05)
            token.cancel()

        # Start cancellation task
        cancel_task = asyncio.create_task(cancel_after_delay())

        # Wait for cancellation
        await token.wait_for_cancellation()

        assert token.is_cancelled
        await cancel_task


class TestOperationCancelledError:
    """Test OperationCancelledError exception."""

    def test_default_message(self):
        error = OperationCancelledError()
        assert str(error) == "Operation cancelled by user"
        assert error.message == "Operation cancelled by user"

    def test_custom_message(self):
        error = OperationCancelledError("Custom cancel message")
        assert str(error) == "Custom cancel message"

    def test_is_exception(self):
        error = OperationCancelledError()
        assert isinstance(error, Exception)


class TestRunCancellable:
    """Test run_cancellable function."""

    @pytest.mark.asyncio
    async def test_operation_completes(self):
        """Test that operation completes normally when not cancelled.

        Note: In test environments, stdin is not a real terminal, so the
        keyboard monitoring loop runs indefinitely. We use asyncio.wait_for
        with a timeout to ensure the test completes.
        """

        async def quick_operation():
            # Very quick operation that should complete before timeout
            return "success"

        # Use timeout because in test env, keyboard monitor runs forever
        result = await asyncio.wait_for(
            run_cancellable(quick_operation(), show_hint=False),
            timeout=1.0,
        )
        assert result == "success"

    @pytest.mark.asyncio
    async def test_operation_returns_value(self):
        """Test that return values are preserved."""

        async def return_dict():
            return {"key": "value", "count": 42}

        result = await asyncio.wait_for(
            run_cancellable(return_dict(), show_hint=False),
            timeout=1.0,
        )
        assert result == {"key": "value", "count": 42}


class TestCancellableContext:
    """Test CancellableContext class."""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test basic context manager usage."""

        async def quick_op():
            return "done"

        async def run_test():
            async with CancellableContext(show_hint=False) as ctx:
                result = await ctx.run(quick_op())
            return result, ctx.was_cancelled

        result, was_cancelled = await asyncio.wait_for(run_test(), timeout=1.0)
        assert result == "done"
        assert not was_cancelled

    @pytest.mark.asyncio
    async def test_multiple_operations(self):
        """Test running multiple operations in sequence."""

        async def op1():
            return 1

        async def op2():
            return 2

        async def op3():
            return 3

        async def run_test():
            async with CancellableContext(show_hint=False) as ctx:
                r1 = await ctx.run(op1())
                r2 = await ctx.run(op2())
                r3 = await ctx.run(op3())
            return r1, r2, r3

        r1, r2, r3 = await asyncio.wait_for(run_test(), timeout=2.0)
        assert r1 == 1
        assert r2 == 2
        assert r3 == 3

    @pytest.mark.asyncio
    async def test_context_preserves_exception(self):
        """Test that non-cancellation exceptions propagate."""

        async def failing_op():
            raise ValueError("Something went wrong")

        async def run_test():
            async with CancellableContext(show_hint=False) as ctx:
                await ctx.run(failing_op())

        with pytest.raises(ValueError, match="Something went wrong"):
            await asyncio.wait_for(run_test(), timeout=1.0)


class TestCancellationIntegration:
    """Integration tests for cancellation behavior."""

    @pytest.mark.asyncio
    async def test_token_cancels_waiting_task(self):
        """Test that cancellation token properly signals waiting tasks."""
        token = CancellationToken()
        results = []

        async def monitored_task():
            for i in range(10):
                if token.is_cancelled:
                    results.append("cancelled")
                    return
                results.append(i)
                await asyncio.sleep(0.01)
            results.append("completed")

        # Start the task
        task = asyncio.create_task(monitored_task())

        # Cancel after a short delay
        await asyncio.sleep(0.025)
        token.cancel()

        await task

        # Should have been cancelled before completing all 10 iterations
        assert "cancelled" in results
        assert "completed" not in results
        assert len(results) < 11

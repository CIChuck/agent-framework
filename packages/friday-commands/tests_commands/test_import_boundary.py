"""Source closure/optimized invariant checks; wheel proof is a separate gate."""

import ast
import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

PACKAGE_SRC = Path(__file__).resolve().parents[1] / "src"


def test_static_dependency_closure_and_runtime_invariants() -> None:
    for path in (PACKAGE_SRC / "friday_commands").glob("*.py"):
        tree = ast.parse(path.read_text())
        assert not any(isinstance(node, ast.Assert) for node in ast.walk(tree))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(
                    alias.name.split(".")[0] in sys.stdlib_module_names
                    for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and not node.level:
                assert node.module.split(".")[0] in sys.stdlib_module_names


def test_fresh_import_blocks_all_nonstdlib_modules() -> None:
    script = dedent(
        f"""
        import sys
        sys.path.insert(0, {str(PACKAGE_SRC)!r})
        class BlockThirdParty:
            def find_spec(self, fullname, path=None, target=None):
                root = fullname.split('.')[0]
                if root != 'friday_commands' and root not in sys.stdlib_module_names:
                    raise ModuleNotFoundError(fullname)
        sys.meta_path.insert(0, BlockThirdParty())
        from friday_commands import CommandRegistry
        if CommandRegistry().names() != frozenset():
            raise RuntimeError('Unexpected default commands')
        try:
            import rich
        except ModuleNotFoundError:
            pass
        else:
            raise RuntimeError('Import guard did not refuse frontend dependency')
        print('Neutral source import passed')
        """
    )
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", script],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Neutral source import passed"


def test_optimized_python_keeps_runtime_validation() -> None:
    script = dedent(
        f"""
        import sys
        sys.path.insert(0, {str(PACKAGE_SRC)!r})
        from friday_commands import (
            CommandArgument, CommandError, CommandExecution, CommandOutcome,
            CommandRequest, CommandSpec, DispatchResult, ExitData,
        )
        cases = [
            (lambda: CommandArgument('a', 'A', required=1), TypeError),
            (lambda: ExitData(1), TypeError),
            (lambda: CommandExecution(17), TypeError),
            (lambda: CommandOutcome(data={{}}), TypeError),
            (lambda: CommandOutcome(), ValueError),
            (lambda: DispatchResult(True, None), ValueError),
            (lambda: CommandError('bad', 'name'), ValueError),
            (lambda: CommandRequest('HELP', (), CommandSpec('help','Help','test','/help')), ValueError),
        ]
        for call, expected in cases:
            try:
                call()
            except Exception as exc:
                if type(exc) is not expected:
                    raise RuntimeError('Wrong optimized exception class') from exc
            else:
                raise RuntimeError('Optimized validation was bypassed')
        print('Optimized invariants passed')
        """
    )
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-O", "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Optimized invariants passed"

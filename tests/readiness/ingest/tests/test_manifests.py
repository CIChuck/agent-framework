"""C0 controls; scratch is explicitly provided by the verified bootstrap."""

from __future__ import annotations

import sys
import unittest
import uuid
from pathlib import Path

from ingest.manifests import (
    Refusal,
    artifact,
    canonical,
    decode,
    dependency_selection,
    digest,
    integer,
    object_value,
    read,
    sequence,
)


def unit() -> Path:
    root: object = getattr(sys.modules["ingest.tests"], "SCRATCH", None)
    if not isinstance(root, Path):
        raise RuntimeError(
            "Use verified bootstrap selftest with explicit private scratch"
        )
    path = root / ("case-" + uuid.uuid4().hex)
    path.mkdir()
    return path


class Manifests(unittest.TestCase):
    def test_dependency_schema_refuses_before_optional_parser_import(self) -> None:
        before = "packaging" in sys.modules
        values: list[object] = [{}, [], {"schema": 2}, {"schema": True}]
        for value in values:
            with self.assertRaises(Refusal):
                dependency_selection(value)
        self.assertEqual("packaging" in sys.modules, before)

    def test_reject_duplicate_nonfinite_and_oversize(self) -> None:
        for raw in (
            b'{"x":1,"x":2}',
            b'{"x":NaN}',
            b'{"x":1e999}',
            b" " * (1024 * 1024 + 1),
            b"[]",
        ):
            with self.subTest(raw=raw[:20]), self.assertRaises(Refusal):
                decode(raw)

    def test_canonical_positive_and_digest_binding(self) -> None:
        root = unit()
        path = root / "record.json"
        path.write_bytes(canonical({"z": [1, 2], "a": "ok"}))
        self.assertEqual(
            read(path, digest(path.read_bytes())), {"a": "ok", "z": [1, 2]}
        )
        with self.assertRaises(Refusal):
            read(path, "0" * 64)

    def test_integer_bool_and_artifact_boundaries(self) -> None:
        with self.assertRaises(Refusal):
            integer(True)
        item = {
            "url": "https://files.pythonhosted.org/a.whl",
            "sha256": "a" * 64,
            "size": 1,
            "license": "MIT",
        }
        self.assertEqual(artifact(item, {"files.pythonhosted.org"}), item)
        for update in (
            {"url": "http://files.pythonhosted.org/a.whl"},
            {"url": "https://key@files.pythonhosted.org/a.whl"},
            {"license": ""},
            {"size": 0},
            {"sha256": "a"},
        ):
            with self.subTest(update=update), self.assertRaises(Refusal):
                artifact(item | update, {"files.pythonhosted.org"})


def dependency_cases() -> dict[str, object]:
    """Explicit offline parser-profile selector, not minimal unittest discovery.

    Invoke only after the approved parser target has been hash-verified and added
    to the private worker's guarded read roots. No resolver, download or install.
    """
    case = unittest.TestCase()

    def wheel(
        name: str, version: str, requires: list[str], extras: list[str]
    ) -> dict[str, object]:
        filename = name.replace("-", "_") + "-" + version + "-py3-none-any.whl"
        return {
            "name": name,
            "version": version,
            "filename": filename,
            "url": "https://files.pythonhosted.org/synthetic/" + filename,
            "sha256": "a" * 64,
            "size": 100,
            "license": "MIT",
            "requires_python": ">=3.10,<3.14",
            "requires_dist": requires,
            "provides_extra": extras,
            "yanked": False,
        }

    value: dict[str, object] = {
        "schema": 1,
        "roots": ["Alpha.File[speed]>=2.4,<3"],
        "environment": {
            "implementation_name": "cpython",
            "implementation_version": "3.13.10",
            "os_name": "posix",
            "platform_machine": "arm64",
            "platform_release": "test",
            "platform_system": "Darwin",
            "platform_version": "test",
            "python_full_version": "3.13.10",
            "platform_python_implementation": "CPython",
            "python_version": "3.13",
            "sys_platform": "darwin",
        },
        "tags": ["py3-none-any", "cp313-cp313-macosx_11_0_arm64"],
        "wheels": [
            wheel(
                "alpha-file",
                "2.4",
                [
                    "Beta>=1,<2",
                    "Gamma; extra == 'speed'",
                    "WindowsOnly; sys_platform == 'win32'",
                ],
                ["speed"],
            ),
            wheel("beta", "1.5", ["Alpha.File>=2.4"], []),
            wheel("gamma", "3.0", [], []),
        ],
    }
    result = dependency_selection(value)
    case.assertEqual(result["status"], "CONSISTENT_CANDIDATE_DECLARATIONS")
    case.assertEqual(result["distribution_count"], 3)
    case.assertEqual(result["selected_bytes"], 300)
    case.assertEqual(object_value(result["requested_extras"])["alpha-file"], ["speed"])
    for name in (
        "artifact_bytes_verified",
        "licenses_qualified",
        "installed_profile_qualified",
        "execution_permitted",
    ):
        case.assertIs(result[name], False)
    case.assertEqual(result, dependency_selection(decode(canonical(value))))
    positives = 1

    def changed_wheel(update: dict[str, object], index: int = 0) -> dict[str, object]:
        altered = decode(canonical(value))
        rows = sequence(altered["wheels"])
        rows[index] = object_value(rows[index]) | update
        altered["wheels"] = rows
        return altered

    negatives: list[dict[str, object]] = [
        changed_wheel({"version": "2.3"}),
        changed_wheel({"filename": "wrong-2.4-py3-none-any.whl"}),
        changed_wheel({"filename": "alpha_file-2.4.tar.gz"}),
        changed_wheel({"filename": "../alpha_file-2.4-py3-none-any.whl"}),
        changed_wheel({"requires_python": "<3.13"}),
        changed_wheel({"requires_python": ""}),
        changed_wheel({"yanked": True}),
        changed_wheel({"yanked": "unknown"}),
        changed_wheel({"url": "https://key@files.pythonhosted.org/a.whl"}),
        changed_wheel(
            {"url": "https://unapproved.invalid/alpha_file-2.4-py3-none-any.whl"}
        ),
        changed_wheel(
            {
                "url": "https://files.pythonhosted.org:8443/alpha_file-2.4-py3-none-any.whl"
            }
        ),
        changed_wheel(
            {
                "url": "https://files.pythonhosted.org/alpha_file-2.4-py3-none-any.whl?x=1"
            }
        ),
        changed_wheel({"size": True}),
        changed_wheel({"size": 4 * 1024**3}),
        changed_wheel(
            {"requires_dist": ["Beta @ https://unapproved.invalid/beta.whl"]}
        ),
        changed_wheel({"requires_dist": ["Beta [broken"]}),
        changed_wheel({"provides_extra": []}),
        changed_wheel({"provides_extra": ["speed", "SPEED"]}),
        changed_wheel({"license": ""}),
        value | {"roots": ["Alpha.File[speed]>=3"]},
        value | {"roots": ["Alpha.File[unknown]"]},
        value | {"roots": ["Missing"]},
        value | {"roots": ["Alpha.File; sys_platform == 'win32'"]},
        value | {"roots": ["Alpha.File [broken"]},
        value | {"tags": ["cp313-cp313-win_amd64"]},
        value | {"tags": ["malformed"]},
        value | {"wheels": sequence(value["wheels"])[:2]},
        value
        | {"wheels": sequence(value["wheels"]) + [wheel("orphan", "1.0", [], [])]},
        value | {"wheels": sequence(value["wheels"]) + [sequence(value["wheels"])[0]]},
        value
        | {
            "environment": object_value(value["environment"])
            | {"python_version": "3.12"}
        },
    ]
    for index, negative in enumerate(negatives):
        with case.subTest(negative=index), case.assertRaises(Refusal):
            dependency_selection(negative)

    no_extra = decode(canonical(value))
    no_extra["roots"] = ["Alpha.File>=2.4"]
    no_extra["wheels"] = sequence(no_extra["wheels"])[:2]
    case.assertEqual(dependency_selection(no_extra)["distribution_count"], 2)
    positives += 1
    native_filename = "gamma-3.0-cp313-cp313-macosx_11_0_arm64.whl"
    native = changed_wheel(
        {
            "filename": native_filename,
            "url": "https://files.pythonhosted.org/" + native_filename,
        },
        2,
    )
    case.assertEqual(dependency_selection(native)["distribution_count"], 3)
    positives += 1
    late_extra = changed_wheel(
        {
            "provides_extra": ["speed"],
            "requires_dist": ["Alpha.File>=2.4", "Alpha.File[speed]; extra == 'speed'"],
        },
        1,
    )
    late_extra["roots"] = ["beta[speed]", "alpha-file"]
    case.assertEqual(
        object_value(dependency_selection(late_extra)["requested_extras"])[
            "alpha-file"
        ],
        ["speed"],
    )
    positives += 1
    prerelease = {**wheel("alpha-file", "2.4rc1", [], []), "requires_python": ">=3.13"}
    rc_selection = value | {"roots": ["alpha-file==2.4rc1"], "wheels": [prerelease]}
    case.assertEqual(dependency_selection(rc_selection)["distribution_count"], 1)
    positives += 1
    with case.assertRaises(Refusal):
        dependency_selection(rc_selection | {"roots": ["alpha-file>=2"]})
    return {
        "positive_cases": positives,
        "refusal_cases": len(negatives) + 1,
        "actual_resolution": False,
        "execution_permitted": False,
    }

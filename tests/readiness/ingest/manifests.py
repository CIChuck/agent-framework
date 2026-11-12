"""Stdlib controls; optional dependency checks require the activated parser."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from urllib.parse import urlsplit

RECORD_LIMIT = 1024 * 1024
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
GIT_ID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


class Refusal(ValueError):
    """An explicit control/qualification refusal, also enforced under -O."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Refusal(reason)


def object_value(value: object) -> dict[str, object]:
    require(isinstance(value, dict), "Expected JSON object")
    if not isinstance(value, dict):
        raise Refusal("Expected JSON object")
    result: dict[str, object] = {}
    for key, item in value.items():
        require(isinstance(key, str), "JSON key is not text")
        if isinstance(key, str):
            result[key] = item
    return result


def text(value: object) -> str:
    if not isinstance(value, str):
        raise Refusal("Expected text")
    return value


def integer(value: object, minimum: int = 0) -> int:
    require(type(value) is int, "Expected integer")
    if type(value) is not int or value < minimum:
        raise Refusal("Integer below boundary")
    return value


def sequence(value: object) -> list[object]:
    if not isinstance(value, list):
        raise Refusal("Expected JSON array")
    return list(value)


def fields(value: object, names: set[str]) -> dict[str, object]:
    result = object_value(value)
    require(set(result) == names, "Missing or unknown control fields")
    return result


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def _pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def _invalid_constant(value: str) -> object:
    raise Refusal("Non-finite JSON constant: " + value)


def decode(data: bytes) -> dict[str, object]:
    require(len(data) <= RECORD_LIMIT, "Control record exceeds 1 MiB")
    try:
        value: object = json.loads(
            data, object_pairs_hook=_pairs, parse_constant=_invalid_constant
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise Refusal("Malformed control JSON") from exc

    # A huge exponent is legal JSON syntax but is not finite control data.
    def finite(item: object, depth: int = 0) -> None:
        require(depth <= 32, "Control nesting limit")
        if isinstance(item, float):
            require(math.isfinite(item), "Non-finite JSON number")
        elif isinstance(item, dict):
            for child in item.values():
                finite(child, depth + 1)
        elif isinstance(item, list):
            for child in item:
                finite(child, depth + 1)

    finite(value)
    return object_value(value)


def read(path: Path, expected: str | None = None) -> dict[str, object]:
    require(path.is_file() and not path.is_symlink(), "Control must be a regular file")
    with path.open("rb") as source:
        data = source.read(RECORD_LIMIT + 1)
    require(expected is None or digest(data) == expected, "Unapproved control digest")
    return decode(data)


def artifact(value: object, hosts: set[str]) -> dict[str, object]:
    result = fields(value, {"url", "sha256", "size", "license"})
    url = urlsplit(text(result["url"]))
    require(url.scheme == "https" and url.hostname in hosts, "Unapproved artifact host")
    require(
        not url.username and not url.password and not url.fragment,
        "Artifact URL has credentials/fragment",
    )
    require(bool(SHA256.fullmatch(text(result["sha256"]))), "Invalid artifact digest")
    integer(result["size"], 1)
    require(bool(text(result["license"]).strip()), "Unresolved artifact license")
    return result


def dependency_selection(value: object) -> dict[str, object]:
    """Check a proposed wheel closure without resolving, downloading or installing.

    The caller must use the separately activated, hash-bound private packaging
    target under the worker guard. A consistent declaration is not artifact,
    license, installed-profile or source-provenance qualification.
    """
    data = fields(value, {"schema", "roots", "environment", "tags", "wheels"})
    require(type(data["schema"]) is int and data["schema"] == 1, "Selection schema")
    roots = sequence(data["roots"])
    wheels = sequence(data["wheels"])
    require(1 <= len(roots) <= 64 and 1 <= len(wheels) <= 512, "Selection count")
    declared = fields(
        data["environment"],
        {
            "implementation_name",
            "implementation_version",
            "os_name",
            "platform_machine",
            "platform_release",
            "platform_system",
            "platform_version",
            "python_full_version",
            "platform_python_implementation",
            "python_version",
            "sys_platform",
        },
    )
    environment = {key: text(item) for key, item in declared.items()}
    require(
        all(0 < len(item) <= 1024 for item in environment.values()),
        "Incomplete explicit marker environment",
    )
    tags = [text(item) for item in sequence(data["tags"])]
    require(1 <= len(tags) <= 2048 and len(set(tags)) == len(tags), "Target tags")

    # Deliberately lazy: C0/core loading and selftests remain standard-library only.
    import packaging
    from packaging.requirements import Requirement
    from packaging.specifiers import SpecifierSet
    from packaging.tags import parse_tag
    from packaging.utils import canonicalize_name, parse_wheel_filename
    from packaging.version import Version

    require(packaging.__version__ == "24.2", "Unqualified standards-parser version")
    try:
        python_version = Version(environment["python_full_version"])
        require(
            environment["python_version"]
            == ".".join(str(part) for part in python_version.release[:2]),
            "Inconsistent explicit Python version",
        )
        try:
            allowed_tags = {tag for item in tags for tag in parse_tag(item)}
        except ValueError as exc:
            raise Refusal("Invalid explicit target wheel tags") from exc
        selected: dict[str, dict[str, object]] = {}
        versions: dict[str, Version] = {}
        dependencies: dict[str, list[Requirement]] = {}
        available_extras: dict[str, set[str]] = {}
        total_bytes = 0
        declared_dependencies = 0

        def requirement(raw: object) -> Requirement:
            value = text(raw)
            require(0 < len(value) <= 4096, "Requirement size")
            parsed = Requirement(value)
            require(parsed.url is None, "Direct-reference dependency refused")
            require(len(parsed.extras) <= 32, "Dependency extra count")
            return parsed

        def active(parsed: Requirement, extra: str) -> bool:
            # Every standard marker field is supplied; no target is inferred
            # from the machine on which this consistency checker happens to run.
            return parsed.marker is None or parsed.marker.evaluate(
                {**environment, "extra": extra}
            )

        for item in wheels:
            row = fields(
                item,
                {
                    "name",
                    "version",
                    "filename",
                    "url",
                    "sha256",
                    "size",
                    "license",
                    "requires_python",
                    "requires_dist",
                    "provides_extra",
                    "yanked",
                },
            )
            name = canonicalize_name(text(row["name"]))
            require(name not in selected, "Duplicate selected distribution")
            version = Version(text(row["version"]))
            filename = text(row["filename"])
            require(Path(filename).name == filename, "Wheel filename path")
            wheel_name, wheel_version, _, wheel_tags = parse_wheel_filename(filename)
            require(
                wheel_name == name and wheel_version == version,
                "Wheel/metadata identity mismatch",
            )
            require(bool(wheel_tags & allowed_tags), "No matching target wheel tag")
            require(row["yanked"] is False, "Yanked/unknown candidate refused")
            checked = artifact(
                {key: row[key] for key in ("url", "sha256", "size", "license")},
                {"files.pythonhosted.org"},
            )
            require(
                urlsplit(text(checked["url"])).path.rsplit("/", 1)[-1] == filename,
                "Wheel URL/filename mismatch",
            )
            url = urlsplit(text(checked["url"]))
            require(url.port in {None, 443} and not url.query, "Unqualified wheel URL")
            requires_python = text(row["requires_python"])
            require(bool(requires_python.strip()), "Unknown Requires-Python")
            require(
                python_version in SpecifierSet(requires_python),
                "Requires-Python excludes explicit target",
            )
            requires_dist = sequence(row["requires_dist"])
            require(len(requires_dist) <= 256, "Distribution dependency count")
            declared_dependencies += len(requires_dist)
            require(declared_dependencies <= 8192, "Declared dependency graph limit")
            dependencies[name] = [requirement(item) for item in requires_dist]
            provided = sequence(row["provides_extra"])
            require(len(provided) <= 64, "Provided extra count")
            available_extras[name] = {
                canonicalize_name(text(item)) for item in provided
            }
            require(
                len(available_extras[name]) == len(provided)
                and all(
                    re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item)
                    for item in available_extras[name]
                ),
                "Invalid/duplicate provided extra",
            )
            total_bytes += integer(row["size"], 1)
            require(total_bytes <= 4 * 1024**3, "Selected package byte ceiling")
            selected[name], versions[name] = row, version

        pending = [parsed for item in roots if active(parsed := requirement(item), "")]
        require(bool(pending), "No active root requirements")
        seen: set[str] = set()
        requested: dict[str, set[str]] = {}
        checked_requirements = 0
        while pending:
            parsed = pending.pop()
            identity = str(parsed)
            if identity in seen:
                continue
            seen.add(identity)
            checked_requirements += 1
            require(checked_requirements <= 8192, "Dependency graph expansion limit")
            name = canonicalize_name(parsed.name)
            require(name in selected, "Missing selected dependency: " + name)
            require(
                versions[name] in parsed.specifier,
                "Selected version violates requirement: " + identity,
            )
            previous = requested.setdefault(name, set())
            requested_names = {canonicalize_name(extra) for extra in parsed.extras}
            require(
                requested_names <= available_extras[name],
                "Unknown requested extra: " + name,
            )
            added = {"", *requested_names} - previous
            previous.update(added)
            for extra in sorted(added):
                pending.extend(dep for dep in dependencies[name] if active(dep, extra))
        require(set(requested) == set(selected), "Unreachable selected distribution")
        return {
            "schema": 1,
            "status": "CONSISTENT_CANDIDATE_DECLARATIONS",
            "selection_sha256": digest(canonical(data)),
            "distribution_count": len(selected),
            "checked_requirements": checked_requirements,
            "selected_bytes": total_bytes,
            "requested_extras": {
                name: sorted(extras - {""})
                for name, extras in sorted(requested.items())
            },
            "artifact_bytes_verified": False,
            "licenses_qualified": False,
            "installed_profile_qualified": False,
            "execution_permitted": False,
        }
    except Refusal:
        raise
    except (ValueError, KeyError) as exc:
        raise Refusal("Invalid dependency declaration: " + type(exc).__name__) from exc

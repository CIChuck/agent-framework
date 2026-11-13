"""Stdlib controls; optional dependency checks require the activated parser."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from time import monotonic
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

if TYPE_CHECKING:
    from packaging.requirements import Requirement
    from packaging.tags import Tag
    from packaging.version import Version

RECORD_LIMIT = 1024 * 1024
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
GIT_ID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
WHEEL_TAG = re.compile(
    r"[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)*-"
    r"[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)*-"
    r"[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)*\Z"
)


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


@dataclass(frozen=True)
class _DependencyInput:
    data: dict[str, object]
    roots: list[object]
    rows: list[object]
    environment: dict[str, str]
    tags: list[str]


def _dependency_input(value: object, row_key: str = "wheels") -> _DependencyInput:
    data = fields(value, {"schema", "roots", "environment", "tags", row_key})
    require(type(data["schema"]) is int and data["schema"] == 1, "Selection schema")
    roots, rows = sequence(data["roots"]), sequence(data[row_key])
    require(1 <= len(roots) <= 64 and 1 <= len(rows) <= 512, "Selection count")
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
    require(
        all(WHEEL_TAG.fullmatch(item) for item in tags),
        "Malformed explicit target wheel tag",
    )
    return _DependencyInput(data, roots, rows, environment, tags)


def _dependency_target(control: _DependencyInput) -> tuple[Version, frozenset[Tag]]:
    import packaging
    from packaging.tags import parse_tag
    from packaging.version import Version

    require(packaging.__version__ == "24.2", "Unqualified standards-parser version")
    python_version = Version(control.environment["python_full_version"])
    require(
        control.environment["python_version"]
        == ".".join(str(part) for part in python_version.release[:2]),
        "Inconsistent explicit Python version",
    )
    return python_version, frozenset(
        tag for item in control.tags for tag in parse_tag(item)
    )


def _dependency_requirement(raw: object) -> Requirement:
    from packaging.requirements import Requirement

    value = text(raw)
    require(0 < len(value) <= 4096, "Requirement size")
    parsed = Requirement(value)
    require(parsed.url is None, "Direct-reference dependency refused")
    require(len(parsed.extras) <= 32, "Dependency extra count")
    return parsed


def _dependency_active(
    parsed: Requirement, environment: dict[str, str], extra: str
) -> bool:
    return parsed.marker is None or parsed.marker.evaluate(
        {**environment, "extra": extra}
    )


@dataclass(frozen=True)
class _DependencyWheel:
    name: str
    version: Version
    key: str
    row: dict[str, object] = field(compare=False, repr=False)
    requirements: tuple[Requirement, ...] = field(compare=False, repr=False)
    extras: frozenset[str] = field(compare=False)
    tags: frozenset[Tag] = field(compare=False, repr=False)
    excluded: tuple[str, ...] = field(compare=False)


def _dependency_wheel(
    value: object, python_version: Version, allowed_tags: frozenset[Tag], strict: bool
) -> _DependencyWheel:
    from packaging.specifiers import SpecifierSet
    from packaging.utils import canonicalize_name, parse_wheel_filename
    from packaging.version import Version

    row = fields(
        value,
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
    name, version = canonicalize_name(text(row["name"])), Version(text(row["version"]))
    filename = text(row["filename"])
    require(Path(filename).name == filename, "Wheel filename path")
    wheel_name, wheel_version, _, tags = parse_wheel_filename(filename)
    require(
        bool(tags) and all(WHEEL_TAG.fullmatch(str(tag)) for tag in tags),
        "Malformed selected wheel tag",
    )
    require(
        wheel_name == name and wheel_version == version,
        "Wheel/metadata identity mismatch",
    )
    if strict:
        require(bool(tags & allowed_tags), "No matching target wheel tag")
        require(row["yanked"] is False, "Yanked/unknown candidate refused")
    require(type(row["yanked"]) is bool, "Yanked/unknown candidate refused")
    checked = artifact(
        {key: row[key] for key in ("url", "sha256", "size", "license")},
        {"files.pythonhosted.org"},
    )
    url = urlsplit(text(checked["url"]))
    require(url.path.rsplit("/", 1)[-1] == filename, "Wheel URL/filename mismatch")
    require(url.port in {None, 443} and not url.query, "Unqualified wheel URL")
    requires_python = text(row["requires_python"])
    require(bool(requires_python.strip()), "Unknown Requires-Python")
    python_matches = python_version in SpecifierSet(requires_python)
    if strict:
        require(python_matches, "Requires-Python excludes explicit target")
    requires_dist = sequence(row["requires_dist"])
    require(len(requires_dist) <= 256, "Distribution dependency count")
    requirements = tuple(_dependency_requirement(item) for item in requires_dist)
    provided = sequence(row["provides_extra"])
    require(len(provided) <= 64, "Provided extra count")
    extras = frozenset(canonicalize_name(text(item)) for item in provided)
    require(
        len(extras) == len(provided)
        and all(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item) for item in extras),
        "Invalid/duplicate provided extra",
    )
    excluded = tuple(
        reason
        for reason, applies in (
            ("platform", not bool(tags & allowed_tags)),
            ("python", not python_matches),
            ("yanked", row["yanked"] is True),
            ("bytes", integer(row["size"], 1) > 4 * 1024**3),
        )
        if applies
    )
    return _DependencyWheel(
        name, version, digest(canonical(row)), row, requirements, extras, tags, excluded
    )


def dependency_selection(value: object) -> dict[str, object]:
    """Check declared wheel closure; optional parser requires its guarded profile."""
    control = _dependency_input(value)
    try:
        from packaging.utils import canonicalize_name

        python_version, allowed_tags = _dependency_target(control)
        selected: dict[str, _DependencyWheel] = {}
        total_bytes = declared_dependencies = 0
        for item in control.rows:
            wheel = _dependency_wheel(item, python_version, allowed_tags, True)
            require(wheel.name not in selected, "Duplicate selected distribution")
            declared_dependencies += len(wheel.requirements)
            require(declared_dependencies <= 8192, "Declared dependency graph limit")
            total_bytes += integer(wheel.row["size"], 1)
            require(total_bytes <= 4 * 1024**3, "Selected package byte ceiling")
            selected[wheel.name] = wheel
        pending = [
            parsed
            for item in control.roots
            if _dependency_active(
                parsed := _dependency_requirement(item), control.environment, ""
            )
        ]
        require(bool(pending), "No active root requirements")
        seen: set[str] = set()
        requested: dict[str, set[str]] = {}
        while pending:
            parsed = pending.pop()
            identity = str(parsed)
            if identity in seen:
                continue
            seen.add(identity)
            require(len(seen) <= 8192, "Dependency graph expansion limit")
            name = canonicalize_name(parsed.name)
            require(name in selected, "Missing selected dependency: " + name)
            wheel = selected[name]
            require(
                wheel.version in parsed.specifier,
                "Selected version violates requirement: " + identity,
            )
            previous = requested.setdefault(name, set())
            extras = {canonicalize_name(extra) for extra in parsed.extras}
            require(extras <= wheel.extras, "Unknown requested extra: " + name)
            added = {"", *extras} - previous
            previous.update(added)
            for extra in sorted(added):
                pending.extend(
                    dep
                    for dep in wheel.requirements
                    if _dependency_active(dep, control.environment, extra)
                )
        require(set(requested) == set(selected), "Unreachable selected distribution")
        return {
            "schema": 1,
            "status": "CONSISTENT_CANDIDATE_DECLARATIONS",
            "selection_sha256": digest(canonical(control.data)),
            "distribution_count": len(selected),
            "checked_requirements": len(seen),
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


@dataclass(frozen=True)
class _ResolutionCandidate:
    wheel: _DependencyWheel
    extras: frozenset[str]


def resolve_catalog(
    value: object,
    *,
    max_rounds: int = 500,
    timeout_seconds: int = 300,
    before_step: Callable[[], None] | None = None,
) -> dict[str, object]:
    """Solve only an explicit closed catalogue. Never fetch, build or install.

    The qualified private worker owns optional imports and external cumulative
    budgets. This call has stricter local bounds and never retries a refusal.
    """
    require(integer(max_rounds, 1) <= 500, "Solver round ceiling")
    require(integer(timeout_seconds, 1) <= 300, "Solver time ceiling")
    started = monotonic()
    require(math.isfinite(started), "Invalid solver clock")

    def checkpoint() -> None:
        now = monotonic()
        require(math.isfinite(now) and now >= started, "Invalid/backward solver clock")
        require(now - started < timeout_seconds, "Solver time exhausted")
        if before_step is not None:
            before_step()
        # A caller callback cannot reopen the time window.
        now = monotonic()
        require(
            math.isfinite(now) and now >= started and now - started < timeout_seconds,
            "Solver time exhausted",
        )

    _dependency_input(value, "candidates")  # Validate shape before optional imports.
    try:
        # Snapshot plain bounded control bytes before a callback can mutate them.
        data = decode(canonical(value))
        control = _dependency_input(data, "candidates")
        checkpoint()
        import packaging
        import resolvelib
        from packaging.requirements import Requirement
        from packaging.utils import canonicalize_name
        from resolvelib import (
            AbstractProvider,
            BaseReporter,
            ResolutionImpossible,
            ResolutionTooDeep,
            Resolver,
        )
        from resolvelib.structs import RequirementInformation

        require(
            packaging.__version__ == "24.2" and resolvelib.__version__ == "1.2.1",
            "Unqualified private solver/parser version",
        )
        python_version, allowed_tags = _dependency_target(control)
        groups: dict[str, list[_DependencyWheel]] = {}
        identities: set[str] = set()
        files: set[str] = set()
        edges = 0
        exclusions: list[dict[str, object]] = []
        for item in control.rows:
            checkpoint()
            wheel = _dependency_wheel(item, python_version, allowed_tags, False)
            require(
                wheel.key not in identities
                and text(wheel.row["filename"]) not in files,
                "Duplicate catalogue wheel",
            )
            identities.add(wheel.key)
            files.add(text(wheel.row["filename"]))
            edges += len(wheel.requirements)
            require(edges <= 8192, "Declared dependency graph limit")
            if wheel.excluded:
                exclusions.append(
                    {
                        "name": wheel.name,
                        "version": str(wheel.version),
                        "filename": wheel.row["filename"],
                        "reasons": list(wheel.excluded),
                    }
                )
            else:
                groups.setdefault(wheel.name, []).append(wheel)
        for name in groups:
            groups[name].sort(
                key=lambda wheel: (wheel.version, wheel.key), reverse=True
            )
        roots = [_dependency_requirement(raw) for raw in control.roots]
        active_roots = [
            req for req in roots if _dependency_active(req, control.environment, "")
        ]
        require(bool(active_roots), "No active root requirements")

        class Provider(AbstractProvider[Requirement, _ResolutionCandidate, str]):
            def identify(
                self, requirement_or_candidate: Requirement | _ResolutionCandidate
            ) -> str:
                checkpoint()
                if isinstance(requirement_or_candidate, _ResolutionCandidate):
                    return requirement_or_candidate.wheel.name
                return canonicalize_name(requirement_or_candidate.name)

            def get_preference(
                self,
                identifier: str,
                resolutions: Mapping[str, _ResolutionCandidate],
                candidates: Mapping[str, Iterator[_ResolutionCandidate]],
                information: Mapping[
                    str,
                    Iterator[RequirementInformation[Requirement, _ResolutionCandidate]],
                ],
                backtrack_causes: Sequence[
                    RequirementInformation[Requirement, _ResolutionCandidate]
                ],
            ) -> str:
                checkpoint()
                return identifier

            def find_matches(
                self,
                identifier: str,
                requirements: Mapping[str, Iterator[Requirement]],
                incompatibilities: Mapping[str, Iterator[_ResolutionCandidate]],
            ) -> list[_ResolutionCandidate]:
                checkpoint()
                constraints = tuple(requirements[identifier])
                extras = frozenset(
                    canonicalize_name(extra)
                    for req in constraints
                    for extra in req.extras
                )
                require(len(extras) <= 64, "Combined solver extra count")
                excluded = set(incompatibilities[identifier])
                result: list[_ResolutionCandidate] = []
                for wheel in groups.get(identifier, []):
                    checkpoint()
                    candidate = _ResolutionCandidate(wheel, extras)
                    if (
                        candidate not in excluded
                        and extras <= wheel.extras
                        and all(wheel.version in req.specifier for req in constraints)
                    ):
                        result.append(candidate)
                return result

            def is_satisfied_by(
                self, requirement: Requirement, candidate: _ResolutionCandidate
            ) -> bool:
                checkpoint()
                return (
                    canonicalize_name(requirement.name) == candidate.wheel.name
                    and candidate.wheel.version in requirement.specifier
                    and {canonicalize_name(extra) for extra in requirement.extras}
                    <= candidate.extras
                )

            def get_dependencies(
                self, candidate: _ResolutionCandidate
            ) -> Iterable[Requirement]:
                checkpoint()
                return tuple(
                    req
                    for req in candidate.wheel.requirements
                    if any(
                        _dependency_active(req, control.environment, extra)
                        for extra in {"", *candidate.extras}
                    )
                )

        class Reporter(BaseReporter[Requirement, _ResolutionCandidate, str]):
            def __init__(self) -> None:
                self.rounds = 0
                self.rejections = 0

            def starting_round(self, index: int) -> None:
                checkpoint()
                self.rounds += 1
                require(
                    index < max_rounds and self.rounds <= max_rounds,
                    "Solver round ceiling",
                )

            def rejecting_candidate(
                self, criterion: object, candidate: _ResolutionCandidate
            ) -> None:
                checkpoint()
                self.rejections += 1

        reporter = Reporter()
        try:
            solved = Resolver(Provider(), reporter).resolve(
                active_roots, max_rounds=max_rounds
            )
        except ResolutionImpossible as exc:
            raise Refusal("Offline catalogue has no compatible solution") from exc
        except ResolutionTooDeep as exc:
            raise Refusal("Solver round ceiling exhausted") from exc
        checkpoint()
        selection: dict[str, object] = {
            "schema": 1,
            "roots": control.data["roots"],
            "environment": control.data["environment"],
            "tags": control.data["tags"],
            "wheels": [
                candidate.wheel.row for _, candidate in sorted(solved.mapping.items())
            ],
        }
        consistent = dependency_selection(selection)
        checkpoint()
        return {
            "schema": 1,
            "status": "SOLVED_CATALOG_DECLARATIONS",
            "catalog_sha256": digest(canonical(control.data)),
            "candidate_count": len(control.rows),
            "selection": selection,
            "consistency": consistent,
            "rounds": reporter.rounds,
            "rejected_candidates": reporter.rejections,
            "excluded_candidates": sorted(
                exclusions, key=lambda row: text(row["filename"])
            ),
            "artifact_bytes_verified": False,
            "licenses_qualified": False,
            "installed_profile_qualified": False,
            "execution_permitted": False,
            "actual_index_resolution": False,
        }
    except Refusal:
        raise
    except (ValueError, KeyError, TypeError, RecursionError) as exc:
        raise Refusal("Invalid catalogue declaration: " + type(exc).__name__) from exc

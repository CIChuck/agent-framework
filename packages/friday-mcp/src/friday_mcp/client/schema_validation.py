"""Bounded, local-only validation for registered MCP tool input schemas."""

from __future__ import annotations

import json
import multiprocessing
from multiprocessing.connection import Connection, wait
from typing import Any, Literal

from jsonschema import Draft7Validator, Draft202012Validator
from referencing import Registry

SchemaDialect = Literal["draft7", "2020-12"]
ArgumentFailureReason = Literal["invalid_arguments", "validation_limit"]


class MCPReferenceError(ValueError):
    """A schema reference cannot be resolved safely within its own document."""


class MCPArgumentValidationError(ValueError):
    """Fixed-message argument failure; never includes peer schema or values."""

    def __init__(self, reason: ArgumentFailureReason = "invalid_arguments") -> None:
        super().__init__("MCP tool arguments failed local validation")
        self.reason = reason


def _escape(segment: str) -> str:
    return segment.replace("~", "~0").replace("/", "~1")


def _pointer(root: dict[str, Any], ref: str) -> tuple[dict[str, Any] | bool, str]:
    if ref == "#":
        return root, "#"
    if not ref.startswith("#/"):
        raise MCPReferenceError("Unsupported MCP reference")
    value: Any = root
    location = "#"
    for segment in ref[2:].split("/"):
        if "~" in segment:
            for index, char in enumerate(segment):
                if char == "~" and (
                    index + 1 >= len(segment) or segment[index + 1] not in "01"
                ):
                    raise MCPReferenceError("Invalid MCP reference escape")
        key = segment.replace("~1", "/").replace("~0", "~")
        location += "/" + _escape(key)
        if isinstance(value, dict):
            if key not in value:
                raise MCPReferenceError("Missing MCP reference target")
            value = value[key]
        elif isinstance(value, list) and (
            key == "0" or (key[:1] in "123456789" and key.isascii() and key.isdecimal())
        ):
            index = int(key)
            if index >= len(value):
                raise MCPReferenceError("Missing MCP reference target")
            value = value[index]
        else:
            raise MCPReferenceError("Missing MCP reference target")
    if not isinstance(value, (dict, bool)):
        raise MCPReferenceError("MCP reference target is not a schema")
    return value, location


def validate_local_references(
    root: dict[str, Any], dialect: SchemaDialect, *, max_refs: int = 128
) -> None:
    """Reject remote/missing refs and cycles without an instance-structure step.

    ``properties``/``items``/``propertyNames``/``additionalProperties`` descend
    into an instance. Combinators and references evaluate the same instance;
    a cycle made solely of those edges cannot terminate safely.
    """
    schemas: dict[int, dict[str, Any] | bool] = {}
    same_instance: dict[int, list[int]] = {}
    refs = 0
    schema_locations: set[str] = set()

    def collect_locations(schema: Any, location: str) -> None:
        if not isinstance(schema, (dict, bool)):
            raise MCPReferenceError("Invalid MCP subschema")
        if location in schema_locations:
            return
        schema_locations.add(location)
        if isinstance(schema, bool):
            return
        for keyword in ("properties", "$defs"):
            for key, child in schema.get(keyword, {}).items():
                collect_locations(child, f"{location}/{keyword}/{_escape(key)}")
        for keyword in ("items", "additionalProperties", "propertyNames", "not"):
            if keyword in schema:
                collect_locations(schema[keyword], f"{location}/{keyword}")
        for keyword in ("allOf", "anyOf", "oneOf"):
            for index, child in enumerate(schema.get(keyword, ())):
                collect_locations(child, f"{location}/{keyword}/{index}")

    collect_locations(root, "#")

    def collect(schema: Any) -> None:
        nonlocal refs
        if isinstance(schema, bool):
            schemas[id(schema)] = schema
            return
        if not isinstance(schema, dict):
            raise MCPReferenceError("Invalid MCP subschema")
        ident = id(schema)
        if ident in schemas:
            return
        schemas[ident] = schema
        edges: list[int] = []
        ref = schema.get("$ref")
        if ref is not None:
            refs += 1
            if refs > max_refs or not isinstance(ref, str):
                raise MCPReferenceError("MCP reference limit")
            target, location = _pointer(root, ref)
            if location not in schema_locations:
                raise MCPReferenceError("MCP reference target is not a schema location")
            edges.append(id(target))
            collect(target)
            if dialect == "draft7" and set(schema) - {"$ref", "title", "description"}:
                raise MCPReferenceError("Draft-07 reference siblings unsupported")
        for keyword in ("allOf", "anyOf", "oneOf"):
            for child in schema.get(keyword, ()):  # Shapes checked by admission.
                collect(child)
                edges.append(id(child))
        if "not" in schema:
            child = schema["not"]
            collect(child)
            edges.append(id(child))
        same_instance[ident] = edges
        for keyword in ("properties", "$defs"):
            for child in schema.get(keyword, {}).values():
                collect(child)
        for keyword in ("items", "additionalProperties", "propertyNames"):
            if keyword in schema:
                collect(schema[keyword])

    collect(root)
    active: set[int] = set()
    done: set[int] = set()
    work = 0

    def visit(ident: int) -> None:
        nonlocal work
        work += 1
        if work > 8192:
            raise MCPReferenceError("MCP reference work limit")
        if ident in active:
            raise MCPReferenceError("MCP reference cycle without instance step")
        if ident in done:
            return
        active.add(ident)
        for child in same_instance.get(ident, ()):
            visit(child)
        active.remove(ident)
        done.add(ident)

    for ident in schemas:
        visit(ident)


def validate_arguments(
    arguments: dict[str, Any], schema: dict[str, Any], dialect: SchemaDialect
) -> None:
    """Validate bounded JSON arguments before any MCP RPC."""
    try:
        encoded = json.dumps(arguments, allow_nan=False, separators=(",", ":"))
        if len(encoded.encode("utf-8")) > 65536:
            raise MCPArgumentValidationError("validation_limit")
        count = 0

        def bound(value: Any, depth: int) -> None:
            nonlocal count
            count += 1
            if depth > 32 or count > 256:
                raise MCPArgumentValidationError("validation_limit")
            if isinstance(value, dict):
                if any(not isinstance(key, str) for key in value):
                    raise MCPArgumentValidationError()
                for child in value.values():
                    bound(child, depth + 1)
            elif isinstance(value, list):
                for child in value:
                    bound(child, depth + 1)

        bound(arguments, 0)
        validator_type = (
            Draft7Validator if dialect == "draft7" else Draft202012Validator
        )
        validator = validator_type(schema, registry=Registry())
        if not validator.is_valid(arguments):
            raise MCPArgumentValidationError()
    except MCPArgumentValidationError:
        raise
    except Exception:
        raise MCPArgumentValidationError() from None


def _validation_worker(
    connection: Connection,
    arguments: dict[str, Any],
    schema: dict[str, Any],
    dialect: SchemaDialect,
) -> None:
    try:
        try:
            validate_arguments(arguments, schema, dialect)
        except MCPArgumentValidationError as exc:
            connection.send(exc.reason)
        except BaseException:
            connection.send("invalid_arguments")
        else:
            connection.send("valid")
    finally:
        connection.close()


def validate_arguments_with_deadline(
    arguments: dict[str, Any],
    schema: dict[str, Any],
    dialect: SchemaDialect,
    *,
    timeout_seconds: float = 2.0,
) -> None:
    """Hard-stop adversarial schema evaluation without leaking input on error."""
    try:
        # Reject oversized/non-JSON input before serializing it to a worker.
        encoded = json.dumps(arguments, allow_nan=False, separators=(",", ":"))
        if len(encoded.encode("utf-8")) > 65536:
            raise MCPArgumentValidationError("validation_limit")
        context = multiprocessing.get_context("spawn")
        receiver, sender = context.Pipe(duplex=False)
        process = context.Process(
            target=_validation_worker,
            args=(sender, arguments, schema, dialect),
            daemon=True,
        )
        try:
            process.start()
            sender.close()
            ready = wait((receiver, process.sentinel), timeout=timeout_seconds)
            if receiver not in ready:
                raise MCPArgumentValidationError("validation_limit")
            outcome = receiver.recv()
            if outcome != "valid":
                reason: ArgumentFailureReason = (
                    "validation_limit"
                    if outcome == "validation_limit"
                    else "invalid_arguments"
                )
                raise MCPArgumentValidationError(reason)
        finally:
            if process.is_alive():
                process.kill()
            if process.pid is not None:
                process.join(timeout=1)
            sender.close()
            receiver.close()
    except MCPArgumentValidationError:
        raise
    except Exception:
        raise MCPArgumentValidationError() from None

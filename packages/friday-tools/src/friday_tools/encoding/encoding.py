"""Encoding tools."""
from __future__ import annotations
import base64
import hashlib
import urllib.parse
import uuid as uuid_lib
from typing import Any
from ..definition import BaseTool


class Base64EncodeTool(BaseTool):
    @property
    def name(self) -> str: return "base64_encode"
    @property
    def description(self) -> str: return "Encode string to base64."
    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}
    async def execute(self, **kwargs: Any) -> str:
        return base64.b64encode(kwargs["text"].encode()).decode()


class Base64DecodeTool(BaseTool):
    @property
    def name(self) -> str: return "base64_decode"
    @property
    def description(self) -> str: return "Decode base64 to string."
    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"encoded": {"type": "string"}}, "required": ["encoded"]}
    async def execute(self, **kwargs: Any) -> str:
        try:
            return base64.b64decode(kwargs["encoded"]).decode()
        except Exception as e:
            return f"Error: {e}"


class HashComputeTool(BaseTool):
    @property
    def name(self) -> str: return "hash_compute"
    @property
    def description(self) -> str: return "Compute hash of text."
    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {
            "text": {"type": "string"},
            "algorithm": {"type": "string", "enum": ["md5", "sha1", "sha256", "sha512"], "default": "sha256"}
        }, "required": ["text"]}
    async def execute(self, **kwargs: Any) -> str:
        algo = kwargs.get("algorithm", "sha256")
        h = hashlib.new(algo)
        h.update(kwargs["text"].encode())
        return h.hexdigest()


class UuidGenerateTool(BaseTool):
    @property
    def name(self) -> str: return "uuid_generate"
    @property
    def description(self) -> str: return "Generate a UUID."
    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"version": {"type": "integer", "default": 4}}, "required": []}
    async def execute(self, **kwargs: Any) -> str:
        return str(uuid_lib.uuid4())


class UrlEncodeTool(BaseTool):
    @property
    def name(self) -> str: return "url_encode"
    @property
    def description(self) -> str: return "URL encode a string."
    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}
    async def execute(self, **kwargs: Any) -> str:
        return urllib.parse.quote(kwargs["text"])


class UrlDecodeTool(BaseTool):
    @property
    def name(self) -> str: return "url_decode"
    @property
    def description(self) -> str: return "URL decode a string."
    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"encoded": {"type": "string"}}, "required": ["encoded"]}
    async def execute(self, **kwargs: Any) -> str:
        return urllib.parse.unquote(kwargs["encoded"])


base64_encode = Base64EncodeTool()
base64_decode = Base64DecodeTool()
hash_compute = HashComputeTool()
uuid_generate = UuidGenerateTool()
url_encode = UrlEncodeTool()
url_decode = UrlDecodeTool()

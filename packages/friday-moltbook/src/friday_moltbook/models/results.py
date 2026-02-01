"""Result models for Moltbook API responses."""

from __future__ import annotations

from pydantic import BaseModel


class RegisterResult(BaseModel):
    api_key: str | None = None
    claim_url: str | None = None
    verification_code: str | None = None

    model_config = {"extra": "allow"}


class ClaimStatus(BaseModel):
    status: str | None = None

    model_config = {"extra": "allow"}


class UploadResult(BaseModel):
    success: bool | None = None
    message: str | None = None

    model_config = {"extra": "allow"}


class DeleteResult(BaseModel):
    success: bool | None = None
    message: str | None = None

    model_config = {"extra": "allow"}


class VoteResult(BaseModel):
    message: str | None = None
    author: dict | None = None
    already_following: bool | None = None
    suggestion: str | None = None

    model_config = {"extra": "allow"}


class FollowResult(BaseModel):
    message: str | None = None
    already_following: bool | None = None

    model_config = {"extra": "allow"}


class SubscribeResult(BaseModel):
    message: str | None = None

    model_config = {"extra": "allow"}


class PinResult(BaseModel):
    message: str | None = None

    model_config = {"extra": "allow"}


class ModeratorResult(BaseModel):
    message: str | None = None

    model_config = {"extra": "allow"}

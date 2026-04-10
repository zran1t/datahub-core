from __future__ import annotations

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """
    共通錯誤細節 payload。
    """

    code: str
    message: str


class ErrorResponse(BaseModel):
    """
    共通錯誤回應 payload。
    """

    error: ErrorDetail


class DatasetCapability(BaseModel):
    """
    dataset-level capability response item。
    """

    name: str
    default_schema_version: str
    query_enabled: bool
    export_enabled: bool
    availability_enabled: bool


class SchemaField(BaseModel):
    """
    schema field response item。
    """

    name: str
    type: str
    description: str
    nullable: bool = False

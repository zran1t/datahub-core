from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from serving_engine.errors.handlers import register_exception_handlers
from serving_engine.routers import candles, info, root


def _build_openapi_schema(app: FastAPI) -> dict[str, Any]:
    """
    產生與目前錯誤處理策略一致的 OpenAPI schema。
    """
    if app.openapi_schema is not None:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    for path_item in schema.get("paths", {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue
            operation.get("responses", {}).pop("422", None)

    component_schemas = schema.get("components", {}).get("schemas", {})
    component_schemas.pop("HTTPValidationError", None)
    component_schemas.pop("ValidationError", None)

    app.openapi_schema = schema
    return schema


def create_app() -> FastAPI:
    """
    建立 serving engine FastAPI app。
    """
    app = FastAPI(
        title="datahub-serving",
        version="v1",
    )
    app.include_router(root.router)
    app.include_router(info.router)
    app.include_router(candles.router)
    register_exception_handlers(app)
    app.openapi = lambda: _build_openapi_schema(app)
    return app

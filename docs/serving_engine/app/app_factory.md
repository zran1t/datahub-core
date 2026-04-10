# App Factory

本文件描述 `app/` 的組裝方式。

## 1. `dependencies.py`

目前提供：

- `get_settings()`
- `get_duckdb_client()`

策略：

- `get_settings()` 使用 process-level cache
- `get_duckdb_client()` 使用 request-scoped `yield`

## 2. `factory.py`

`create_app()` 目前負責：

- 建立 FastAPI app
- include routers
- register exception handlers
- 覆寫 OpenAPI，移除已不使用的 FastAPI 預設 `422` validation schema

## 3. `main.py`

`main.py` 只保留：

```python
app = create_app()
```

它是純 ASGI entrypoint，不放 CLI 或其他組裝邏輯。

# Request Flow

本文件描述 `serving_engine` v1 目前已落地的 request flow。

## 1. Candles Rows Query

```text
GET /v1/data/candles
  -> router (`routers/candles.py`)
  -> service (`services/candles_service.py`)
  -> query (`query/candles_query.py`)
  -> DuckDB client (`query/duckdb_client.py`)
  -> canonical parquet
  -> service result dict
  -> schema (`schemas/candles.py`)
  -> JSON response
```

責任切分：

- router：接 query params、注入 settings / client、套 response model
- service：補預設、驗證參數、時間字串轉 ms、DataFrame -> `list[dict]`
- query：path resolve、SQL、rows query

## 2. Candles Export

```text
GET /v1/data/candles/export
  -> router (`routers/candles.py`)
  -> service (`services/candles_service.py`)
  -> query (`query/candles_query.py`)
  -> DuckDB `COPY TO`
  -> parquet file
  -> FileResponse
```

這條路徑不走 JSON schema。

## 3. Info Endpoints

### Version / Dataset / Schema

```text
GET /v1/info/version
GET /v1/info/datasets
GET /v1/info/schemas/{dataset}/{schema_version}
  -> router (`routers/info.py`)
  -> service (`services/info_service.py`)
  -> catalog (`catalog/*.py`)
  -> schema (`schemas/info.py`)
  -> JSON response
```

### Availability

```text
GET /v1/info/availability/candles
  -> router (`routers/info.py`)
  -> service (`services/info_service.py`)
  -> availability query (`query/availability_query.py`)
  -> schema (`schemas/info.py`) or `None`
  -> JSON response
```

## 4. Error Flow

```text
service/query raise exception
  -> FastAPI app
  -> `errors/handlers.py`
  -> `ErrorResponse`
```

目前 v1 主要收斂：

- `ValueError` -> `400 INVALID_ARGUMENT`
- `FileNotFoundError` -> `404 NO_DATA`
- `RequestValidationError` -> `400 INVALID_ARGUMENT`
- unexpected `Exception` -> `500 INTERNAL_ERROR`

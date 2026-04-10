# Routers

本文件描述 `routers/` 的角色與目前結構。

## 1. 設計原則

router 是純 HTTP layer，只做：

- 接 request
- 注入 dependencies
- 呼叫 service
- 映射到 schema / `FileResponse`

不做：

- SQL
- parquet path
- business validation
- error mapping

## 2. `root.py`

提供：

- `/v1`
- `/v1/info`
- `/v1/data`

這三個 endpoint 直接回固定 dict，不走 service。

## 3. `info.py`

接：

- `services/info_service.py`
- `schemas/info.py`
- `get_settings()`

對應：

- `/v1/info/version`
- `/v1/info/datasets`
- `/v1/info/schemas/{dataset}/{schema_version}`
- `/v1/info/availability/candles`

## 4. `candles.py`

接：

- `services/candles_service.py`
- `schemas/candles.py`
- `get_settings()`
- `get_duckdb_client()`

對應：

- `/v1/data/candles`
- `/v1/data/candles/export`

`export` endpoint 只做 `symbols.split(",")`，其餘 normalize 與驗證交給 service。

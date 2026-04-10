# Info Service

本文件描述 `services/info_service.py` 的角色。

## 1. 定位

`info_service.py` 是 metadata / self-description use-case layer。

它負責把：

- `catalog/*`
- `query/availability_query.py`
- 少量固定 version metadata

整理成 `/v1/info/*` 需要的 service-level payload。

## 2. Public API

目前提供：

- `get_version_info()`
- `get_supported_datasets()`
- `get_schema_info(...)`
- `get_candles_availability_info(...)`

## 3. Version / Dataset / Schema

這三條路徑都依賴 catalog：

- dataset existence / capability -> `datasets.py`
- schema lookup -> `schema_registry.py`

service 自己不維護 registry 常數。

## 4. Candles Availability

`get_candles_availability_info(...)` 的流程：

1. settings 補 `exchange` / `interval`
2. 驗證目前僅支援 `okx` / `1m`
3. normalize `symbol`
4. call `get_candles_availability(...)`
5. `None -> None`
6. result -> service-level dict

## 5. 不做的事

- DuckDB
- rows query
- parquet content scan
- HTTP response object
- error envelope

# API Schemas

本文件描述 `schemas/` 在 `serving_engine` 中的角色。

## 1. 定位

`schemas/` 是 API response schema layer。

它只定義：

- JSON response payload shape
- 共用 error / dataset / field schema

它不定義：

- dataset contract 本體
- query logic
- service orchestration
- request parsing model

## 2. `common.py`

目前包含：

- `ErrorDetail`
- `ErrorResponse`
- `DatasetCapability`
- `SchemaField`

`common.py` 應保持克制，不要變成雜物箱。

## 3. `candles.py`

目前包含：

- `CandleRow`
- `CandlesQueryResponse`

注意：

- `CandleRow` 不帶 `symbol`
- `symbol` 在 envelope 同層

## 4. `info.py`

目前包含：

- `VersionInfoResponse`
- `SupportedDatasetsResponse`
- `SchemaInfoResponse`
- `CandlesAvailabilityResponse`

其中 `SchemaInfoResponse` 目前保留：

- `time_semantics: dict[str, Any]`
- `symbol_rules: dict[str, Any]`
- `interval_constraints: dict[str, Any]`

第一版不再拆更多子 model。

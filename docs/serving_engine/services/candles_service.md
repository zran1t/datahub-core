# Candles Service

本文件描述 `services/candles_service.py` 的角色。

## 1. 定位

`candles_service.py` 是 candles API use-case layer。

它負責把：

- `ServingSettings`
- `DuckDBClient`
- `query/candles_query.py`

組成兩個 use cases：

- `get_candles(...)`
- `export_candles(...)`

## 2. 主要責任

- 補預設 `exchange` / `interval`
- 驗證目前只支援 `okx` / `1m`
- 驗證單 symbol rows query
- 驗證 `start < end`
- 驗證 / 套用 `limit`
- 將 ISO8601 轉成 UTC ms
- `DataFrame -> list[dict]`
- 生成 export output path

## 3. `get_candles(...)`

輸入：

- 單一 `symbol`
- `start` / `end`
- optional `exchange` / `interval`
- optional `limit`

輸出：

- service-level `dict`

行為：

- `limit=None` 時自動套 `json_query_max_rows`
- `start` / `end` 回傳為 normalized UTC `...Z`
- rows 空結果時回 `rows=0`、`data=[]`

## 4. `export_candles(...)`

輸入：

- `symbols: Sequence[str]`
- `start` / `end`

輸出：

- 匯出檔案 `Path`

行為：

- 支援 `1+ symbols`
- path 一律由 service 端產生
- 不在 service 內建立 `FileResponse`

## 5. 不做的事

- SQL
- parquet file discovery
- HTTP response object
- API error payload
- Pydantic response model

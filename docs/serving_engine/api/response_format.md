# Response Format

本文件描述 `serving_engine` v1 的回應格式。

## 1. Root Index Endpoints

以下 endpoints 直接回固定 dict：

- `/v1`
- `/v1/info`
- `/v1/data`

它們不使用獨立 schema model。

## 2. JSON Success Responses

目前主要 JSON success shape：

- `VersionInfoResponse`
- `SupportedDatasetsResponse`
- `SchemaInfoResponse`
- `CandlesAvailabilityResponse`
- `CandlesQueryResponse`

## 3. Candles Rows Payload

`/v1/data/candles` 回傳：

- dataset / schema_version metadata
- exchange / symbol / interval
- normalized `start` / `end`
- `rows`
- `data`

其中：

- `rows == len(data)`
- row 內不重複輸出 `symbol`

## 4. Availability Payload

`/v1/info/availability/candles` 有兩種情況：

- 有資料：`CandlesAvailabilityResponse`
- 無資料：`null`

這裡的 `null` 是 use-case 結果，不是另一種 envelope。

## 5. File Responses

`/v1/data/candles/export` 直接回檔案下載，不走 JSON schema。

目前固定：

- 單一 parquet 檔
- `content-type: application/octet-stream`
- `filename=path.name`

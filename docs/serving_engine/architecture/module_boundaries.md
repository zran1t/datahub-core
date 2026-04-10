# Module Boundaries

本文件定義 `serving_engine` 內各層的責任邊界，目標是避免資料邏輯、HTTP 邏輯與 runtime config 混雜。

## 1. Query Layer

`query/` 只負責 data access。

應放：

- canonical physical layout 解析
- parquet day partition 掃描
- DuckDB SQL 組裝
- rows query
- parquet export
- availability metadata query

不應放：

- 預設值補齊
- API request / response envelope
- FastAPI `Response`
- error code mapping
- auth / rate limiting

## 2. Services

`services/` 只負責 use case orchestration 與產品規則。

應放：

- 補預設 `exchange` / `interval`
- 驗證 `start < end`
- 驗證 `limit`
- 判斷 `format` / `layout` 是否支援
- 呼叫 query layer
- 將 DataFrame 轉成 API 可用資料結構

不應放：

- parquet path 拼接
- DuckDB SQL
- FastAPI route 定義

## 3. Catalog

`catalog/` 只負責 serving metadata registry。

應放：

- 支援哪些 dataset
- dataset schema metadata
- schema version registry

不應放：

- parquet query
- runtime settings
- API payload model

## 4. Settings

`settings/` 只負責 runtime config 與 path resolve。

應放：

- canonical root
- export root
- DuckDB connect config
- JSON query row limit
- `@dorma/...` dev alias resolve

不應放：

- mkdir side effects
- parquet query
- business validation

## 5. Errors

`errors/` 只負責 API error surface。

應放：

- error code 定義
- domain error -> HTTP error mapping
- 統一錯誤 payload 格式

不應放：

- query 邏輯
- dataset contract

## 6. Routers

`routers/` 只負責 HTTP layer。

應放：

- route path
- query params 解析
- response model 綁定
- 將請求轉交 service

不應放：

- DuckDB SQL
- parquet path 掃描
- 大量產品規則

## 7. App

`app/` 只負責組裝 FastAPI runtime。

應放：

- app factory
- dependency wiring
- router 掛載
- exception handler 註冊

不應放：

- dataset-specific logic
- rows query / export 細節

## 8. 當前對齊原則

目前 `serving_engine` 採這組基本原則：

- query 層不要補預設
- service 層不要拼 parquet path
- settings 層不要查資料
- router 層保持薄
- query 與 availability 分離，不硬抽 generic base layer

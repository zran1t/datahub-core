> Legacy draft.
> Superseded by [`docs/serving_engine/api/api_v1.md`](serving_engine/api/api_v1.md).
> Do not extend this file further.

# DataHub API v1 規格

## 1. 文件目的
本文檔定義 datahub 的 v1 HTTP API 介面規格。
v1 目標是提供統一、穩定、可程式化存取的歷史市場資料入口。

v1 僅涵蓋 canonical dataset 的讀取，不包含 raw dataset，也不包含寫入操作。

---

## 2. v1 範圍

v1 API 提供：

- 唯讀資料查詢
- 批次資料匯出
- API 自我描述（info endpoints）

v1 僅支援 dataset：
- candles

v1 不包含：

- raw dataset 存取
- 任意 SQL 查詢
- 即時資料
- 寫入 / 更新 / 刪除操作

---

## 3. 設計原則

### 3.1 Canonical-only
API 僅提供 canonical dataset。

### 3.2 Parquet-first
Parquet 為主要資料交付格式，JSON 僅用於小量查詢。

### 3.3 Read-only
所有 API 為唯讀操作。

### 3.4 Dataset-first
API 以 dataset 為核心，不提供任意查詢語言。

---

## 4. URL 結構

```
/v1
/v1/info
/v1/data

/v1/info/version
/v1/info/datasets
/v1/info/schemas/{dataset}/{schema_version}
'/v1/info/availability/{dataset}'

/v1/data/candles
'/v1/data/candles/export'
```

---

## 5. 通用約定

### 5.1 時間格式
- request: ISO8601 UTC
- dataset: epoch milliseconds

### 5.2 時間區間
- start: inclusive
- end: exclusive
- 必須滿足 start < end

### 5.3 排序
預設依時間升冪排序

### 5.4 空資料
- 回傳 200 OK
- data: []
- rows: 0

### 5.5 查詢方式
所有查詢使用 GET + query parameters

---

## 6. 認證（預留）

v1 初版不強制認證。
未來將使用：

Authorization: Bearer <token>

---

## 7. API 入口

### 7.1 GET /v1
回傳 API 分類入口

### 7.2 GET /v1/info
回傳資訊類 endpoint 列表

### 7.3 GET /v1/data
回傳資料類 endpoint 列表

---

## 8. 資訊類 API

### 8.1 GET /v1/info/version
回傳 API 版本資訊

### 8.2 GET /v1/info/datasets
回傳支援 dataset 列表

### 8.3 GET /v1/info/schemas/{dataset}/{schema_version}
回傳 schema 定義

### 8.4 GET /v1/info/availability/{dataset}
查詢資料可用範圍

---

## 9. 資料類 API

### 9.1 GET /v1/data/candles

用途：小量查詢

參數：
- exchange
- symbol
- interval
- start
- end
- limit
- format=json

---

### 9.2 GET /v1/data/candles/export

用途：批次匯出

參數：
- exchange
- symbols
- interval
- start
- end
- format=parquet
- layout=single_file

---

## 10. 回應格式

### JSON

```
{
  "dataset": "candles",
  "schema_version": "v1",
  "rows": 0,
  "data": []
}
```

---

## 11. 錯誤格式

```
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "..."
  }
}
```

---

## 12. 版本策略

- /v1 為 API major version
- schema version 由 dataset 定義
- schema 改變需升版本

---

## 13. 與 dataset contract 的關係

本文件定義 API 行為。

dataset 細節見：
- candles.md

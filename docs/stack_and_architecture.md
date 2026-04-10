> Legacy draft.
> Superseded by [`docs/serving_engine/README.md`](serving_engine/README.md) and [`docs/serving_engine/architecture/overview.md`](serving_engine/architecture/overview.md).
> Do not extend this file further.

# DataHub 技術棧與架構方向（v1）

## 1. 專案定位

datahub v1 為一個基於 canonical dataset 的歷史資料服務，主要目標為：

- 提供穩定、可程式化的資料存取介面
- 支援研究與回測系統
- 提供高效率的批次資料下載能力

v1 僅支援：
- candles dataset（1m）

---

## 2. 核心技術棧

### 2.1 Parquet（資料層）

角色：
- canonical dataset 的主要儲存格式
- 系統的唯一資料來源

特性：
- columnar storage
- schema 明確
- 高壓縮比
- 適合時間序列與分析型查詢

說明：
Parquet 為 datahub 的資料核心，不是中繼格式，而是最終資料層。

---

### 2.2 DuckDB（查詢層）

角色：
- embedded query engine
- 負責查詢 parquet dataset

用途：
- filter（symbol / time range）
- projection（選擇欄位）
- ordering（排序）
- 多檔案合併

說明：
DuckDB 僅作為查詢引擎，不負責 API、認證或服務邏輯。

---

### 2.3 FastAPI（服務層）

角色：
- HTTP API 層
- 將 dataset 封裝為 API

用途：
- 定義路由（/v1/info, /v1/data）
- 解析 query parameters
- 驗證請求
- 回傳 JSON 或檔案

說明：
FastAPI 僅負責 API interface，不負責資料抓取或轉換。

---

### 2.4 Uvicorn（執行層）

角色：
- ASGI server
- 執行 FastAPI 應用

---

## 3. 系統分層

```
Client
  ↓
HTTP API (FastAPI)
  ↓
Service Layer
  ↓
Data Access Layer (DuckDB)
  ↓
Canonical Dataset (Parquet)
```

---

## 4. 子系統劃分

### 4.1 Ingestion / Sync
- 從交易所抓取資料
- 補齊歷史資料
- 寫入 raw dataset

### 4.2 Normalization
- raw → canonical
- 型別轉換
- 過濾未完成資料

### 4.3 API Service
- 提供資料查詢與匯出
- 不負責資料生成

---

## 5. 資料邊界

- canonical dataset 為唯一對外資料來源
- raw dataset 不對外提供
- backtest engine 與 datahub 共用 canonical dataset

---

## 6. API 設計方向

- 採用 RESTful GET API
- 查詢條件透過 query parameters 表達
- JSON 用於小量查詢
- Parquet 用於 bulk export

---

## 7. v1 不包含內容

- 即時資料（streaming）
- 任意 SQL 查詢
- 多格式 export（CSV 暫不支援）
- 高併發分散式架構
- 完整認證與權限系統

---

## 8. 未來擴展方向

- 支援更多 dataset（trades, orderbook）
- 增加 interval（5m, 1h 等）
- 引入資料驗證與完整性檢查工具
- 加入認證與 rate limiting
- CDN cache 整合

---

## 9. 設計總結

- Parquet 為資料核心
- DuckDB 為查詢引擎
- FastAPI 為 API 介面
- canonical dataset 為系統共享邊界
- ingestion / normalization / serving 分離

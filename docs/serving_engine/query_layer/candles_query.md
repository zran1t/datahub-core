# Candles Query

本文件描述 `query/candles_query.py` 的設計定位與行為策略。

## 1. 定位

`candles_query.py` 是 `candles` dataset 的 data-access module。

它只負責：

- 小量 rows query
- 大量 parquet export
- canonical day partition path resolve
- DuckDB SQL 組裝與執行

它不負責：

- 預設值補齊
- `limit` 上限決策
- `format` / `layout` 產品規則
- API response envelope
- FastAPI / HTTP 物件

## 2. Public API

目前對外只有兩個 public functions：

- `query_candles_rows(...)`
- `export_candles_to_parquet(...)`

這兩個 function 都只接收已決定好的最終參數，不接受半成品請求語意。

## 3. Rows Query

`query_candles_rows(...)` 的定位：

- 單 symbol
- 小量 rows query
- 回傳 pandas DataFrame

行為約定：

- 根據 `start_ms` / `end_ms` 映射到需掃描的 UTC 日檔
- 只讀取實際存在的 parquet files
- 無任何檔案時回傳欄位固定的空 DataFrame
- 固定輸出 canonical row fields
- 不在 row 內重複輸出 `symbol`
- 固定 `ORDER BY ts ASC`

## 4. Export Query

`export_candles_to_parquet(...)` 的定位：

- 多 symbol
- bulk export
- 直接輸出單一 parquet 檔

行為約定：

- 只對有資料的 symbol 建立 export source
- 所有來源都沒有資料時報錯
- 匯出前建立輸出目錄
- 直接使用 DuckDB `COPY (...) TO ... (FORMAT PARQUET, COMPRESSION ZSTD)`
- 不走 DataFrame 再寫 parquet
- 固定輸出 `symbol` 欄位
- 固定 `ORDER BY symbol ASC, ts ASC`

## 5. Path Resolve 策略

`candles_query.py` 了解 canonical candles 的 physical layout：

```text
<root>/<exchange>/<symbol>/<interval>/<year>/<month>/YYYY-MM-DD.parquet
```

這份 knowledge 屬於 dataset-specific query responsibility，不應放入：

- `DuckDBClient`
- service
- router

## 6. 時間語意

rows query 與 export 都採：

- `start` inclusive
- `end` exclusive

query 會先將時間範圍映射成需掃描的 UTC 日分片，再以 SQL 條件限制最終 row 範圍。

## 7. 空資料策略

rows query 與 export 故意採不同策略：

- rows query：無資料回空 DataFrame
- export：所有來源都無資料時報錯

這是因為兩者代表不同 use case：

- rows query 更像一般資料查詢
- export 是較重的明確匯出動作

## 8. 安全與輸入原則

query layer 的基本原則：

- user scalar values 盡量使用參數綁定
- parquet path list 只允許 server 端 resolve
- 不接受 client 提供檔案路徑
- 不提供 user-controlled sort / selected columns

## 9. 非目標

目前 v1 不在 `candles_query.py` 內提供：

- multi-symbol rows query
- CSV export
- Arrow export
- generic dataset base query layer
- completeness checks
- caching

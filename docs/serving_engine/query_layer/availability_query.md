# Availability Query

本文件描述 `query/availability_query.py` 的定位與行為。

## 1. 定位

`availability_query.py` 是一個 metadata-style query module。

它只回答：

- 某個 `exchange + symbol + interval` 的資料大致可用範圍是什麼

它不回答：

- 中間是否有缺洞
- 實際 completeness 如何
- 每一天是否完整

## 2. Public API

目前只提供：

- `get_candles_availability(...) -> CandlesAvailability | None`

其中 `CandlesAvailability` 包含：

- `exchange`
- `symbol`
- `interval`
- `available_start_ms`
- `available_end_ms`

找不到任何合法日檔時回傳 `None`。

## 3. 為什麼不使用 DuckDB

availability v1 的目標是輕量 metadata 查詢，不是 row query。

因此目前設計刻意：

- 不依賴 DuckDB
- 不讀 parquet 內容
- 不做 `min(ts)` / `max(ts)` 聚合

它只根據 canonical day partition file presence 推導 availability。

## 4. 推導方式

目前流程為：

1. 根據 `root / exchange / symbol / interval` 找出 symbol-interval 目錄
2. 掃描符合 canonical 命名規則的日 parquet 檔
3. 從檔名解析出日期
4. 取最早日檔與最晚日檔
5. 轉成 availability start / end

其中：

- `available_start_ms` = 最早一天的 `00:00:00Z`
- `available_end_ms` = 最晚一天的下一天 `00:00:00Z`

## 5. End-exclusive 語意

`available_end_ms` 明確採 end-exclusive 語意。

例如若最後一個檔是 `2025-01-31.parquet`，則：

- `available_end_ms = 2025-02-01T00:00:00Z`

這樣可與 API 其他地方的 `start` / `end` contract 保持一致。

## 6. 檔名規則

目前 availability 只依賴 canonical day file naming：

- `YYYY-MM-DD.parquet`

它不把目前的 physical directory layout 視為對外契約，避免未來 partition 結構調整時產生不必要耦合。

## 7. 非目標

目前 v1 不在 `availability_query.py` 內提供：

- missing days list
- completeness ratio
- partition validation
- multi-symbol aggregation
- parquet content inspection

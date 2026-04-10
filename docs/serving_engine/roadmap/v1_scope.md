# Serving Engine v1 Scope

本文件只列出 `serving_engine` v1 明確包含與不包含的內容。

## 1. v1 會做

- canonical-only historical data serving
- read-only API
- dataset self-description
- candles dataset
- `1m` interval
- 單 symbol rows query
- 多 symbol parquet export
- dataset availability metadata

## 2. v1 不做

- multi-symbol rows query
- realtime / streaming
- CSV export
- arbitrary SQL
- auth / authorization
- rate limiting
- completeness checks
- missing days query
- multi-file export layout
- raw dataset access

## 3. v1 的刻意限制

v1 先以最小可用產品為目標，重點是：

- 先把 canonical dataset 查詢能力做穩
- 先把 query / service / router 邊界固定
- 先支援最必要的 candles serving surface

其他能力留待後續版本擴展。

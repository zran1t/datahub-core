# Candles Dataset Contract

本文件定義 `serving_engine` 對 `candles` canonical dataset 的資料契約理解。

## 1. 資料集定位

`candles` 是 historical OHLCV canonical dataset，用於：

- 研究分析
- 回測引擎
- datahub serving

資料來源來自交易所歷史資料，經 canonical normalization 後提供給整個平台共用。

## 2. Canonical Schema

| 欄位 | 型別 | 說明 |
| --- | --- | --- |
| `ts` | `int64` | UTC epoch milliseconds，代表 candle open time |
| `open` | `float64` | 開盤價 |
| `high` | `float64` | 最高價 |
| `low` | `float64` | 最低價 |
| `close` | `float64` | 收盤價 |
| `vol` | `float64` | 成交量 |
| `volCcy` | `float64` | 基礎幣成交量 |
| `volCcyQuote` | `float64` | 計價幣成交量 |

所有欄位皆為 non-null。

## 3. 時間語意

- `ts` 表示 candle open time
- timezone 一律為 UTC
- 單位一律為 epoch milliseconds
- 所有資料依 `ts` 升冪排序

## 4. Interval 規則

- v1 僅支援 `1m`
- 每筆資料代表 1 分鐘區間
- 不同 interval 不混用

## 5. Symbol 規則

使用 canonical symbol naming，例如：

- `BTC-USDT-SPOT`
- `BTC-USDT-SWAP`

說明：

- symbol 大小寫敏感
- raw exchange symbol 不屬於公開契約

## 6. Closed Candle 規則

- canonical dataset 只包含已完成的 candles
- raw 中 `confirm != 1` 的資料不會進入 canonical dataset
- canonical schema 不包含 `confirm`

## 7. Volume 欄位

以下欄位都屬於必要資訊：

- `vol`
- `volCcy`
- `volCcyQuote`

三者不可互相完整推導，因此 canonical dataset 全數保留。

## 8. 唯一性與品質

- `(exchange, symbol, interval, ts)` 應唯一
- 不應存在重複 candle
- canonical dataset 不補值
- canonical dataset 不生成 synthetic rows

資料完整性與補洞屬於資料 pipeline / sync 領域，不是 serving query 的責任。

## 9. Physical Layout（實作參考）

目前 canonical candles 採日分片 parquet：

```text
data/canonical/candle/{exchange}/{symbol}/{interval}/{year}/{month}/YYYY-MM-DD.parquet
```

這是內部 physical layout，供 query layer 實作參考，不屬於 public API contract。

## 10. 與 Serving 行為的關係

serving v1 對 `candles` 的目前約定：

- 單 symbol rows query 的 row 不重複包含 `symbol`
- 多 symbol parquet export 會補出 `symbol` 欄位作為資料識別
- availability 以 day partition file presence 推導，採 start-inclusive / end-exclusive 語意

這些屬於 serving behavior 與 dataset contract 的交界，但不是 route 細節。

## 11. 版本策略

本文件定義的是 `candles` schema version `v1`。

以下變更需要升版：

- 欄位刪除
- 欄位語意改變
- 欄位型別改變

以下變更不需升版：

- 資料時間範圍擴展
- 新增 partition
- 日檔數量增加

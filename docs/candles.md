> Legacy draft.
> Superseded by [`docs/serving_engine/datasets/candles.md`](serving_engine/datasets/candles.md).
> Do not extend this file further.

# Candles Dataset Contract

## 1. 文件目的
本文檔定義 `candles` canonical dataset 的資料契約。

本文件描述：
- 資料欄位與語意
- 時間與區間定義
- symbol 規則
- 資料品質與約束

本文件不包含：
- raw dataset 定義
- ingestion / normalization 流程
- API endpoint 規格（見 api_v1.md）

---

## 2. 資料集定位

`candles` 為歷史 OHLCV canonical dataset，用於：

- 研究分析
- 回測引擎
- 資料分發（datahub）

資料來源目前為交易所歷史資料（例如 OKX），並經 canonical normalization 處理。

---

## 3. Canonical Schema

| 欄位 | 型別 | 說明 |
|------|------|------|
| ts | int64 | UTC 毫秒時間戳，代表 candle open time |
| open | float64 | 開盤價 |
| high | float64 | 最高價 |
| low | float64 | 最低價 |
| close | float64 | 收盤價 |
| vol | float64 | 成交量 |
| volCcy | float64 | 基礎幣成交量 |
| volCcyQuote | float64 | 計價幣成交量 |

所有欄位皆為 non-null。

---

## 4. 時間語意

- `ts` 表示 candle open time
- timezone 為 UTC
- 單位為 milliseconds (epoch ms)
- 所有資料依 `ts` 升冪排序

---

## 5. Interval 規則

- v1 僅定義 `1m` interval
- 每筆資料代表 1 分鐘區間
- interval 為 dataset partition 的一部分
- 不同 interval 不混用

---

## 6. Symbol 規則

- 使用 canonical symbol naming
- 格式為：
  - `BTC-USDT-SPOT`
  - `BTC-USDT-SWAP`
- symbol 大小寫敏感
- raw exchange symbol 不屬於公開契約

---

## 7. Closed Candle 規則

- 僅包含已完成（closed）的 candles
- raw 中 `confirm != 1` 的資料不進入 canonical dataset
- canonical schema 不包含 `confirm` 欄位

---

## 8. Volume 欄位

以下欄位均保留：

- `vol`
- `volCcy`
- `volCcyQuote`

三者不可互相推導，均為必要資訊。

---

## 9. 排序與唯一性

- 資料依 `ts` 升冪排序
- `(exchange, symbol, interval, ts)` 應唯一
- 不應存在重複 candle

---

## 10. 資料品質與完整性

- canonical dataset 不進行補值
- 不生成 synthetic rows
- completeness 由資料驗證流程負責維護
- 若資料存在缺口，應透過 pipeline 修正

---

## 11. 儲存布局（實作參考）

```
data/canonical/candle/{exchange}/{symbol}/{interval}/{year}/{month}/YYYY-MM-DD.parquet
```

- 每檔為單一 UTC 日
- 此為內部儲存布局，不屬於公開 API 契約

---

## 12. 與 DataHub API 的關係

本 dataset 透過以下 API 提供：

- `/v1/data/candles`
- `/v1/data/candles/export`

API 行為與參數定義見 `api_v1.md`。

---

## 13. 版本策略

本文件定義 `candles` schema version `v1`。

以下變更需升版：
- 欄位刪除
- 欄位語意改變
- 型別改變

以下不需升版：
- 新增資料
- 擴展時間範圍

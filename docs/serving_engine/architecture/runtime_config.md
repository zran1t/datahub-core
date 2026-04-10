# Runtime Config

本文件描述 `serving_engine/settings/config.py` 的角色與目前 v1 使用的 runtime config。

## 1. 角色

`settings/config.py` 負責：

- 載入 serving engine 所需的最小設定
- 將設定中的路徑解析為實際 `Path`
- 提供本地開發與部署環境共用的設定入口

它不負責：

- 查 parquet
- 建立 export 目錄
- 補 query 預設值以外的業務邏輯

## 2. `ServingSettings`

目前 `ServingSettings` 包含：

| 欄位 | 用途 |
| --- | --- |
| `canonical_candle_root` | canonical candles dataset 根目錄 |
| `export_root` | export 輸出根目錄 |
| `default_exchange` | v1 convenience default |
| `default_interval` | v1 convenience default |
| `json_query_max_rows` | 小量 JSON 查詢上限 |
| `duckdb_database` | DuckDB 連線目標，預設 `:memory:` |
| `duckdb_read_only` | DuckDB read-only flag |
| `duckdb_config` | DuckDB 額外連線設定 |

## 3. 環境變數

目前支援：

| 環境變數 | 預設值 |
| --- | --- |
| `DATAHUB_CANONICAL_CANDLE_ROOT` | `@dorma/data/canonical/candle` |
| `DATAHUB_EXPORT_ROOT` | `@dorma/workspace/datahub_exports` |
| `DATAHUB_DEFAULT_EXCHANGE` | `okx` |
| `DATAHUB_DEFAULT_INTERVAL` | `1m` |
| `DATAHUB_JSON_QUERY_MAX_ROWS` | `10000` |
| `DATAHUB_DUCKDB_DATABASE` | `:memory:` |
| `DATAHUB_DUCKDB_READ_ONLY` | `false` |

## 4. 路徑解析規則

目前 settings 支援三種路徑輸入：

- `@dorma/...`
- 絕對路徑
- 相對路徑

解析規則：

- `@dorma/...`：相對於 dorma root 解析
- 絕對路徑：直接使用
- 相對路徑：相對於目前 process working directory 解析

## 5. `@dorma/...` 的定位

`@dorma/...` 是本地開發便利 alias，不是部署契約。

正式部署時應優先使用：

- `DORMA_ROOT`
- 或直接提供絕對路徑 env vars

這個原則特別重要，因為 `serving_engine` 長期目標是可部署到 Ubuntu / Linux 環境，而不是綁定目前開發 workspace。

## 6. 開發與部署心智模型

本地開發時：

- 可使用 `@dorma/...`
- 可依靠 workspace root 推斷路徑

部署環境中：

- 應以明確 env vars 為準
- 應優先提供絕對路徑
- 不應假設目前工作目錄或 IDE workspace

## 7. 與 query / service 的關係

settings 提供：

- canonical root
- export root
- DuckDB config

service 使用：

- `default_exchange`
- `default_interval`
- `json_query_max_rows`

query 使用：

- resolved `Path`
- DuckDB 連線設定

目前約定：

- settings 不做 mkdir
- export 寫檔前再建立目錄

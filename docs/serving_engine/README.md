# Serving Engine

`serving_engine` 是 `datahub-core` 內負責對外提供 canonical dataset 的歷史資料服務邊界。

目前 v1 的目標是：

- 以 canonical dataset 作為唯一資料來源
- 提供穩定、可程式化的歷史資料讀取介面
- 支援小量 JSON 查詢與大量 Parquet 匯出
- 保持 read-only、dataset-first、parquet-first

目前已落地的模組：

- `settings/config.py`
- `query/duckdb_client.py`
- `query/candles_query.py`
- `query/availability_query.py`
- `catalog/`
- `services/`
- `schemas/`
- `errors/`
- `routers/`
- `app/`
- `runner/`

## 本機啟動

安裝 editable package：

```bash
cd cores/datahub-core
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

啟動 API：

```bash
DORMA_ROOT=/Users/tingan/Documents/dorma \
  .venv/bin/datahub-serving --host 127.0.0.1 --port 8000
```

執行測試：

```bash
.venv/bin/pytest
```

## 文檔導覽

- 架構總覽：[`architecture/overview.md`](architecture/overview.md)
- 模組責任邊界：[`architecture/module_boundaries.md`](architecture/module_boundaries.md)
- request flow：[`architecture/request_flow.md`](architecture/request_flow.md)
- runtime config：[`architecture/runtime_config.md`](architecture/runtime_config.md)
- v1 API 總覽：[`api/api_v1.md`](api/api_v1.md)
- info endpoints：[`api/info_endpoints.md`](api/info_endpoints.md)
- data endpoints：[`api/data_endpoints.md`](api/data_endpoints.md)
- response format：[`api/response_format.md`](api/response_format.md)
- error model：[`api/error_model.md`](api/error_model.md)
- candles dataset contract：[`datasets/candles.md`](datasets/candles.md)
- catalog registry：[`catalog/registry.md`](catalog/registry.md)
- DuckDB client：[`query_layer/duckdb_client.md`](query_layer/duckdb_client.md)
- candles query：[`query_layer/candles_query.md`](query_layer/candles_query.md)
- availability query：[`query_layer/availability_query.md`](query_layer/availability_query.md)
- candles service：[`services/candles_service.md`](services/candles_service.md)
- info service：[`services/info_service.md`](services/info_service.md)
- routers：[`app/routers.md`](app/routers.md)
- schemas：[`app/schemas.md`](app/schemas.md)
- app factory：[`app/app_factory.md`](app/app_factory.md)
- runner CLI：[`runner/cli.md`](runner/cli.md)
- v1 scope：[`roadmap/v1_scope.md`](roadmap/v1_scope.md)

## 與舊文檔的關係

根目錄下原有的：

- `docs/stack_and_architecture.md`
- `docs/api_v1.md`
- `docs/candles.md`

目前視為 legacy draft，只作早期契約與設計脈絡參考。正式 serving engine 文檔以本目錄為準。

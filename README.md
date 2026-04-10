# datahub-core

`datahub-core` 是 `dorma` 平台中的資料服務 core，目前主要承載 `serving_engine`。

## 本機開發

在 `datahub-core` 目錄內建立獨立虛擬環境並安裝：

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

啟動 CLI 說明：

```bash
.venv/bin/datahub-serving --help
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

## 文件入口

- [serving_engine 文件首頁](docs/serving_engine/README.md)

# Runner CLI

本文件描述 `runner/cli.py` 的定位。

## 1. 定位

`datahub-serving` 是 `serving_engine` 的本機啟動入口。

它只是對 `uvicorn serving_engine.app.main:app` 的薄包裝。

## 2. 目前支援參數

- `--host`
- `--port`
- `--reload`
- `--log-level`

## 3. 目標

它的目的是讓本機開發與手動驗證更穩定，而不是承擔部署平台責任。

第一版不處理：

- process management
- env file orchestration
- deploy metadata

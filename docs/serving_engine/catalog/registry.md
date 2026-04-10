# Catalog Registry

本文件描述 `catalog/` 在 `serving_engine` 中的角色。

## 1. 定位

`catalog/` 是 serving metadata registry，不是 query layer。

它提供兩類 truth source：

- dataset-level capability metadata
- schema metadata

## 2. `datasets.py`

`datasets.py` 負責：

- 哪些 dataset 受支援
- 每個 dataset 的 capability
- default schema version

目前 `DatasetInfo` 包含：

- `name`
- `default_schema_version`
- `query_enabled`
- `export_enabled`
- `availability_enabled`

## 3. `schema_registry.py`

`schema_registry.py` 負責：

- dataset/schema_version 是否存在
- schema field metadata
- time semantics 摘要
- symbol rules 摘要
- interval constraints 摘要

它不重寫整份 dataset 文檔，只保存 API/info endpoint 需要的結構化摘要。

## 4. 與 Service 的關係

`info_service.py` 應依賴：

- `datasets.py` 處理 dataset existence / capability
- `schema_registry.py` 處理 schema lookup

service 不再維護第二份 registry truth。

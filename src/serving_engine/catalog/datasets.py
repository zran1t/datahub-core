from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DatasetInfo:
    """
    Serving engine dataset-level capability metadata。
    """

    name: str
    default_schema_version: str
    query_enabled: bool
    export_enabled: bool
    availability_enabled: bool


_DATASETS: dict[str, DatasetInfo] = {
    "candles": DatasetInfo(
        name="candles",
        default_schema_version="v1",
        query_enabled=True,
        export_enabled=True,
        availability_enabled=True,
    ),
}


def list_supported_datasets() -> list[DatasetInfo]:
    """
    列出目前支援的 datasets，順序固定依 registry 定義。
    """
    return list(_DATASETS.values())


def get_dataset_info(name: str) -> DatasetInfo | None:
    """
    依名稱取得 dataset metadata。
    """
    return _DATASETS.get(name)


def is_supported_dataset(name: str) -> bool:
    """
    判斷指定 dataset 是否受支援。
    """
    return name in _DATASETS


def get_default_schema_version(name: str) -> str | None:
    """
    取得 dataset 的預設 schema version。
    """
    dataset = get_dataset_info(name)
    if dataset is None:
        return None
    return dataset.default_schema_version

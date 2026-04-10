# Error Model

本文件描述 `serving_engine` v1 的統一錯誤模型。

## 1. Payload Shape

所有 API 錯誤都收斂成：

```json
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "..."
  }
}
```

對應 schema：

- `ErrorDetail`
- `ErrorResponse`

## 2. 目前使用中的 Error Codes

- `INVALID_ARGUMENT`
- `NO_DATA`
- `INTERNAL_ERROR`

已保留但第一版 handler 尚未直接發出的常數：

- `UNSUPPORTED_DATASET`
- `SCHEMA_NOT_FOUND`

## 3. Exception Mapping

目前 runtime mapping：

- `ValueError` -> `400 INVALID_ARGUMENT`
- `FileNotFoundError` -> `404 NO_DATA`
- `RequestValidationError` -> `400 INVALID_ARGUMENT`
- unexpected `Exception` -> `500 INTERNAL_ERROR`

## 4. Request Validation

`serving_engine` 已將 FastAPI request validation errors 收斂到自己的 error payload。

也就是：

- runtime 不直接回 FastAPI 預設 `422` payload
- OpenAPI 也移除了預設 `422 / HTTPValidationError` schema

## 5. Internal Error Policy

`500` 錯誤目前固定回：

- `code = INTERNAL_ERROR`
- `message = "Internal server error"`

不把 traceback 或內部檔案路徑回給 client。

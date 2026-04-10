from __future__ import annotations

import argparse
from collections.abc import Sequence

import uvicorn


def build_parser() -> argparse.ArgumentParser:
    """
    建立 serving_engine CLI parser。
    """
    parser = argparse.ArgumentParser(description="Run the datahub serving engine API.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind.")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload.")
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Uvicorn log level.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """
    啟動 serving_engine ASGI app。
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    uvicorn.run(
        "serving_engine.app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

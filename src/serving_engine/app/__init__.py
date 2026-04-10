"""
ASGI app assembly for serving_engine.
"""

from serving_engine.app.factory import create_app

__all__ = ["create_app"]

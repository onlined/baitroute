from fastapi import FastAPI

from . import BaitRoute
from .starlette_integration import BaitRouteMiddleware


def register_with_fastapi(app: FastAPI, baitroute: BaitRoute) -> None:
    """Register bait endpoints with a FastAPI application.

    Args:
        app: FastAPI application instance
        baitroute: BaitRoute instance containing the rules
    """
    app.add_middleware(BaitRouteMiddleware, baitroute=baitroute)

from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from . import BaitRoute


class BaitRouteMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, baitroute: BaitRoute):
        super().__init__(app)
        self.baitroute = baitroute

    async def dispatch(self, request: Request, call_next: Callable):
        rule = self.baitroute.get_matching_rule(request.url.path, request.method)
        if rule:
            # Send alert if handler is configured
            if self.baitroute.alert_handler is not None:
                body = None
                if request.headers.get("content-type") == "application/json":
                    body = await request.json()
                elif request.headers.get("content-type") == "application/x-www-form-urlencoded":
                    body = await request.form()
                else:
                    body = await request.body()
                    if body:
                        body = body.decode()

                alert = self.baitroute.create_alert(
                    path=str(request.url.path),
                    method=request.method,
                    remote_addr=request.client.host,
                    headers=dict(request.headers),
                    body=body
                )
                self.baitroute.alert_handler(alert)

            # Return response according to rule
            headers = {'Content-Type': rule.get('content-type', 'text/plain')}
            if 'headers' in rule:
                headers.update(rule['headers'])

            return Response(
                content=rule.get('body', ''),
                status_code=rule.get('status', 200),
                headers=headers
            )

        return await call_next(request)

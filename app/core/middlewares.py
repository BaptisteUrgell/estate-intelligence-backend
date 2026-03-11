import time
import uuid

import structlog
from opentelemetry import trace
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = structlog.get_logger()


class ASGILoggingMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Only process HTTP requests
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        structlog.contextvars.clear_contextvars()
        request = Request(scope)
        span = trace.get_current_span()
        start_time = time.perf_counter()

        trace_id = None
        if span and span.is_recording():
            trace_id = format(span.get_span_context().trace_id, "032x")

        structlog.contextvars.bind_contextvars(
            correlation_id=request.headers.get("x-correlation-id", str(uuid.uuid4())),
            trace_id=trace_id,
            path=request.url.path,
            method=request.method,
        )

        status_code = 500

        async def wrapped_send(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)
            await send(message)

        try:
            await self.app(scope, receive, wrapped_send)
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            # Canonical Log Line
            logger.info(
                "request_completed", status_code=status_code, duration_ms=round(duration_ms, 2)
            )

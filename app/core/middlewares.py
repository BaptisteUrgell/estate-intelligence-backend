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

        correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))

        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
            trace_id=trace_id,
            path=request.url.path,
            method=request.method,
        )

        status_code = 500
        response_started = False

        async def wrapped_send(message: Message) -> None:
            nonlocal status_code, response_started
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, wrapped_send)
        except Exception as exc:
            logger.exception("unhandled_system_crash", exc_info=exc)
            if not response_started:
                from fastapi import status
                from fastapi.responses import JSONResponse

                response = JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "type": "about:blank",
                        "title": "Internal Server Error",
                        "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "detail": "An unexpected technical failure occurred.",
                        "instance": f"urn:uuid:{correlation_id}",
                    },
                    headers={"Content-Type": "application/problem+json"},
                )
                await response(scope, receive, send)
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            else:
                raise exc
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            # Canonical Log Line
            logger.info(
                "request_completed", status_code=status_code, duration_ms=round(duration_ms, 2)
            )

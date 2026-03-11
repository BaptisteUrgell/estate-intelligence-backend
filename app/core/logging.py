import logging
import sys
from typing import Any

import structlog


def redact_pii_processor(
    logger: structlog.types.WrappedLogger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    sensitive_keys = {"password", "token", "api_key", "credit_card", "ssn", "authorization"}
    for key in sensitive_keys:
        if key in event_dict:
            event_dict[key] = "[REDACTED]"
    return event_dict


def setup_logging() -> None:
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        redact_pii_processor,  # Custom PII masking
    ]

    if sys.stderr.isatty():
        # LOCAL: Human-readable, aligned, and colorful output
        processors = shared_processors + [structlog.dev.ConsoleRenderer()]
    else:
        # PRODUCTION: Machine-readable JSON for log aggregators
        processors = shared_processors + [structlog.processors.JSONRenderer()]

    structlog.configure(
        processors=processors,  # type: ignore
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

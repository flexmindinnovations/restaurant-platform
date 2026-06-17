import logging
import sys
from collections.abc import MutableMapping
from typing import Any

import structlog
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from shared.api.middleware.request_id import request_id_ctx_var


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structlog to format logs as JSON and inject Request-ID context."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    def request_id_processor(
        _logger: Any, _log_method: str, event_dict: MutableMapping[str, Any]
    ) -> MutableMapping[str, Any]:
        req_id = request_id_ctx_var.get()
        if req_id:
            event_dict["request_id"] = req_id
        return event_dict

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            request_id_processor,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def setup_telemetry(app: FastAPI, settings: Any) -> None:
    """Initialize OpenTelemetry tracer provider, OTLP exporter, and instrument dependencies."""
    # Build instrumentation resources
    resource = Resource.create(
        attributes={
            "service.name": settings.otel_service_name,
            "environment": settings.app_env,
        }
    )

    # Setup global tracer provider
    provider = TracerProvider(resource=resource)

    # Setup the OTLP Exporter (defaults to gRPC based on OTEL_EXPORTER_OTLP_ENDPOINT)
    exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)

    # Instrument various libraries
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument()
    RedisInstrumentor().instrument()
    CeleryInstrumentor().instrument()  # type: ignore[no-untyped-call]

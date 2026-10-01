import logging
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class TracingService:
    """
    Manages OpenTelemetry tracing context across distributed Celery tasks.
    """
    
    @staticmethod
    def inject_context(headers: Dict[str, str]) -> Dict[str, str]:
        """Inject current trace context into carrier headers (e.g., Celery task headers)."""
        TraceContextTextMapPropagator().inject(headers)
        return headers

    @staticmethod
    def extract_context(headers: Dict[str, str]):
        """Extract trace context from carrier headers."""
        context = TraceContextTextMapPropagator().extract(headers)
        if context:
            trace.get_tracer(__name__).start_as_current_span(
                "extracted_task", context=context
            )
            
    @staticmethod
    def start_span(name: str):
        """Start a new span within the current trace."""
        tracer = trace.get_tracer(__name__)
        return tracer.start_as_current_span(name)
        
    @staticmethod
    def get_correlation_id() -> Optional[str]:
        """Get current trace ID for logging correlation."""
        span = trace.get_current_span()
        if span and span.get_span_context().is_valid:
            return format(span.get_span_context().trace_id, "032x")
        return None

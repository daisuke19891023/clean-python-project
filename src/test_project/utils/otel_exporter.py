"""OpenTelemetry log exporter implementations following SOLID principles.

This module provides abstract interfaces and concrete implementations for
exporting logs to various destinations including local files and OTLP endpoints.
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import structlog
try:
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter as OTLPLogsExporter  # type: ignore[import-not-found]
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler  # type: ignore[import-not-found]
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor  # type: ignore[import-not-found]
    from opentelemetry.sdk.resources import Resource
    OTEL_AVAILABLE = True
except ImportError:
    # OpenTelemetry not available
    OTLPLogsExporter = Any  # type: ignore[misc,assignment]
    LoggerProvider = Any  # type: ignore[misc,assignment]
    LoggingHandler = Any  # type: ignore[misc,assignment]
    BatchLogRecordProcessor = Any  # type: ignore[misc,assignment]
    Resource = Any  # type: ignore[misc,assignment]
    OTEL_AVAILABLE = False
from structlog.types import EventDict

from test_project.utils.settings import LoggingSettings, OTelExportMode


class LogExporter(ABC):
    """Abstract base class for log exporters (Interface Segregation Principle).

    This interface defines the contract that all log exporters must implement.
    """

    @abstractmethod
    def export(self, event_dict: EventDict) -> None:
        """Export a log event.

        Args:
            event_dict: The log event dictionary to export

        """
        ...

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the exporter and release resources."""
        ...


class FileLogExporter(LogExporter):
    """Exports logs to a local file (Single Responsibility Principle).

    This class is responsible only for writing logs to files.
    """

    def __init__(self, file_path: str) -> None:
        """Initialize the file exporter.

        Args:
            file_path: Path to the log file

        """
        self.file_path = Path(file_path)
        self._logger = structlog.get_logger(__name__)

        # Ensure directory exists
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            self._logger.error("Failed to create log directory", error=str(e))

    def export(self, event_dict: EventDict) -> None:
        """Export log event to file.

        Args:
            event_dict: The log event to write

        """
        try:
            with self.file_path.open("a", encoding="utf-8") as f:
                json.dump(event_dict, f, ensure_ascii=False)
                f.write("\n")
        except OSError as e:
            self._logger.error(
                "Failed to write log to file",
                file_path=str(self.file_path),
                error=str(e),
            )

    def shutdown(self) -> None:
        """Shutdown the file exporter."""
        # File exporter doesn't need explicit cleanup


class OTLPLogExporter(LogExporter):
    """Exports logs to an OTLP endpoint (Single Responsibility Principle).

    This class is responsible only for sending logs to OTLP collectors.
    """

    _otlp_exporter: Any
    _provider: Any
    _otel_logger: Any

    def __init__(
        self,
        endpoint: str,
        service_name: str = "python-app",
        timeout: int = 30000,
    ) -> None:
        """Initialize the OTLP exporter.

        Args:
            endpoint: OTLP collector endpoint
            service_name: Name of the service
            timeout: Export timeout in milliseconds

        """
        self.endpoint = endpoint
        self.service_name = service_name
        self.timeout = timeout
        self._logger = structlog.get_logger(__name__)

        if not OTEL_AVAILABLE:
            self._logger.warning(
                "OpenTelemetry not available, OTLP export will be disabled",
                endpoint=endpoint,
            )
            self._provider = None
            self._otel_logger = None
            self._otlp_exporter = None
            return

        # Create resource
        resource = Resource.create(
            {
                "service.name": service_name,
                "service.version": "1.0.0",
            },
        )

        # Initialize OTLP exporter
        try:
            self._otlp_exporter = OTLPLogsExporter(
                endpoint=endpoint,
                timeout=timeout // 1000,  # Convert to seconds
            )

            # Set up logger provider
            self._provider = LoggerProvider(resource=resource)  # type: ignore[misc]
            processor: Any = BatchLogRecordProcessor(self._otlp_exporter)  # type: ignore[misc]
            self._provider.add_log_record_processor(processor)  # type: ignore[misc]

            # Get logger for exporting
            self._otel_logger = self._provider.get_logger(__name__)  # type: ignore[misc]

        except Exception as e:
            self._logger.error(
                "Failed to initialize OTLP exporter",
                endpoint=endpoint,
                error=str(e),
            )
            raise

    def export(self, event_dict: EventDict) -> None:
        """Export log event to OTLP endpoint.

        Args:
            event_dict: The log event to send

        """
        if not OTEL_AVAILABLE or not self._otel_logger:
            return

        try:
            # Extract level and message
            level = event_dict.get("level", "info").upper()
            message = event_dict.get("event", "")

            # Remove internal fields and prepare attributes
            attributes = {
                k: v for k, v in event_dict.items()
                if k not in {"event", "level", "_record", "_from_structlog"}
            }

            # Note: severity mapping is not needed for current implementation
            # but kept here for potential future use with structured logging

            # Log using OpenTelemetry logger
            log_method = getattr(
                self._otel_logger, level.lower(), self._otel_logger.info,
            )
            log_method(message, extra={"attributes": attributes})

        except Exception as e:
            self._logger.error(
                "Failed to export log to OTLP",
                endpoint=self.endpoint,
                error=str(e),
            )

    @property
    def provider(self) -> Any:
        """Get the logger provider for testing purposes."""
        return self._provider

    def shutdown(self) -> None:
        """Shutdown the OTLP exporter."""
        try:
            if hasattr(self, "_provider"):
                self._provider.shutdown()
        except Exception as e:
            self._logger.error("Error during OTLP exporter shutdown", error=str(e))


class LogExporterFactory:
    """Factory for creating log exporters (Factory Pattern + Dependency Inversion).

    This factory creates appropriate exporters based on configuration,
    allowing the system to depend on abstractions rather than concrete classes.
    """

    @staticmethod
    def create(settings: LoggingSettings) -> list[LogExporter]:
        """Create log exporters based on settings.

        Args:
            settings: Application logging settings

        Returns:
            List of configured log exporters

        """
        exporters: list[LogExporter] = []

        # Create file exporter if needed
        if settings.otel_logs_export_mode in (
            OTelExportMode.FILE,
            OTelExportMode.BOTH,
        ) and settings.log_file_path:
            exporters.append(FileLogExporter(settings.log_file_path))

        # Create OTLP exporter if needed
        if settings.otel_logs_export_mode in (
            OTelExportMode.OTLP,
            OTelExportMode.BOTH,
        ):
            try:
                exporters.append(
                    OTLPLogExporter(
                        endpoint=settings.otel_endpoint,
                        service_name=settings.otel_service_name,
                        timeout=settings.otel_export_timeout,
                    ),
                )
            except Exception as e:
                logger = structlog.get_logger(__name__)
                logger.error(
                    "Failed to create OTLP exporter",
                    endpoint=settings.otel_endpoint,
                    error=str(e),
                )

        return exporters


class StructlogOTelProcessor:
    """Structlog processor for OpenTelemetry export (Open/Closed Principle).

    This processor integrates with structlog's processing chain and can be
    extended without modifying existing logger configuration.
    """

    def __init__(self, exporters: list[LogExporter]) -> None:
        """Initialize the processor with exporters.

        Args:
            exporters: List of log exporters to use

        """
        self.exporters = exporters
        self._logger = structlog.get_logger(__name__)

    def __call__(
        self,
        logger: Any,  # noqa: ARG002
        method_name: str,  # noqa: ARG002
        event_dict: EventDict,
    ) -> EventDict:
        """Process log event and export it.

        Args:
            logger: The logger instance
            method_name: The logging method name
            event_dict: The event dictionary

        Returns:
            The unmodified event dictionary

        """
        # Export to all configured exporters
        for exporter in self.exporters:
            try:
                exporter.export(event_dict)
            except Exception as e:
                # Log error but don't fail the logging operation
                self._logger.error(
                    "Failed to export log",
                    exporter=type(exporter).__name__,
                    error=str(e),
                )

        return event_dict

    def shutdown(self) -> None:
        """Shutdown all exporters."""
        for exporter in self.exporters:
            try:
                exporter.shutdown()
            except Exception as e:
                self._logger.error(
                    "Error shutting down exporter",
                    exporter=type(exporter).__name__,
                    error=str(e),
                )

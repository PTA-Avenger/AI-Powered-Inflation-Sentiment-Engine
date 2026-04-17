"""Logging configuration and utilities."""

import logging
import logging.config
from datetime import datetime
import json
from config import get_settings


def setup_logging():
    """Configure structured logging."""
    settings = get_settings()
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(timestamp)s %(level)s %(name)s %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "json" if settings.log_format == "json" else "standard",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.log_level,
                "formatter": "json" if settings.log_format == "json" else "standard",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["console", "file"],
        },
    }
    
    logging.config.dictConfig(config)


class StructuredLogger:
    """Structured logging helper."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_event(self, event: str, **kwargs):
        """Log structured event."""
        log_data = {
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs,
        }
        self.logger.info(json.dumps(log_data))

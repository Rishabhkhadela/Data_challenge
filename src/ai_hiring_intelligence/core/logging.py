import json
import logging
import sys
from typing import Any


class JsonLikeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = getattr(record, "extra", None)
        if isinstance(extra, dict):
            base.update(extra)
        return json.dumps(base, default=str)


def configure_logging(level: str = "INFO", json_logs: bool = True) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLikeFormatter() if json_logs else logging.Formatter("%(message)s"))

    logging.basicConfig(
        level=level.upper(),
        handlers=[handler],
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_extra(**kwargs: Any) -> dict[str, Any]:
    return {"extra": kwargs}

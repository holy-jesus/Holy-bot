import json
import logging
from datetime import datetime, timezone

from loguru import logger

class ValkeyHandler(logging.Handler):
    def __init__(self, client, key="logs", timeout=0.01):
        super().__init__()
        self.client = client
        self.key = key
        self.timeout = timeout

    def emit(self, record: logging.LogRecord):
        try:
            log = {
                "timestamp": datetime.fromtimestamp(
                    record.created, timezone.utc
                ).isoformat(),
                "level": record.levelname.lower(),
                "service": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "func": record.funcName,
                "line": record.lineno,
            }

            if record.exc_info:
                log["exception"] = self.formatException(record.exc_info)

            self.client.lpush(self.key, json.dumps(log))

        except Exception:
            # НИКОГДА не даём логгеру уронить приложение
            pass

import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "nivel": record.levelname,
                "mensagem": record.getMessage(),
            },
            ensure_ascii=False,
        )


def obter_logger(nome: str = "conversas_ia") -> logging.Logger:
    logger = logging.getLogger(nome)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

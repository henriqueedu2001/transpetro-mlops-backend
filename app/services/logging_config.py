import logging
from pathlib import Path


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("transpetro")
    logger.setLevel(logging.INFO)
    if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_dir / "system.log", encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s level=%(levelname)s component=%(name)s %(message)s")
        )
        logger.addHandler(handler)
    return logger

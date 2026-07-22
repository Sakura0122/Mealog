import logging
import sys

from loguru import logger

from src.core.config import settings

_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


class InterceptHandler(logging.Handler):
    """将标准库日志转发给 Loguru。"""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame = logging.currentframe()
        depth = 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, "{}", record.getMessage())


def setup_logger() -> None:
    settings.logger_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.add(
        sys.stderr,
        format=_LOG_FORMAT,
        level=settings.logger_level,
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
    logger.add(
        settings.logger_dir / "mealog.log",
        format=_LOG_FORMAT,
        level=settings.logger_level,
        rotation="00:00",
        retention="30 days",
        compression="gz",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        encoding="utf-8",
    )

    intercept_handler = InterceptHandler()
    logging.basicConfig(
        handlers=[intercept_handler],
        level=settings.logger_level,
        force=True,
    )

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        std_logger = logging.getLogger(name)
        std_logger.handlers = [intercept_handler]
        std_logger.propagate = False

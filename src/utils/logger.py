import json
import logging
import sys


class JsonFormatter(logging.Formatter):
    """
    Formats log records as a JSON string.
    Handles the 'extra' parameter to include custom fields.
    """

    def format(self, record: logging.LogRecord) -> str:
        # These are the standard attributes from a LogRecord
        standard_keys = {
            "args",
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "message",
            "module",
            "msecs",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
            "taskName",
        }

        # Base log object with standard information
        log_object = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            # "logger_name": record.name,
            "message": record.getMessage(),
        }

        # Add any fields passed in the 'extra' parameter
        for key, value in record.__dict__.items():
            if key not in standard_keys:
                log_object[key] = value

        return json.dumps(log_object, ensure_ascii=False)


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a logger with a JSON formatter.
    """
    logger = logging.getLogger(name)
    logger.handlers.clear()  # Prevents adding handlers multiple times
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger


if __name__ == "__main__":
    logger = setup_logger("test_logger")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

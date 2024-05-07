import ast
import json
import logging
import os
import sys
import traceback
from datetime import datetime
from functools import wraps

LOG_LEVEL = os.getenv("LOG_LEVEL", default="INFO")
LOG_APP_NAME = os.getenv("LOG_APP_NAME", default="app")
LOG_FORMAT = os.getenv("LOG_FORMAT", default="str")  # set to json for json format logs


class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.

    @param dict fmt_dict: Key: logging format attribute pairs. Defaults to {"message": "message"}.
    @param str time_format: time.strftime() format string. Default: "%Y-%m-%dT%H:%M:%S"
    @param str msec_format: Microsecond formatting. Appended at the end. Default: "%s.%03dZ"
    """

    def __init__(
        self,
        fmt_dict: dict = None,
        time_format: str = "%Y-%m-%dT%H:%M:%S",
        msec_format: str = "%s.%03dZ",
    ):
        self.fmt_dict = fmt_dict if fmt_dict is not None else {"message": "message"}
        self.default_time_format = time_format
        self.default_msec_format = msec_format
        self.datefmt = None

    def usesTime(self) -> bool:
        """
        Overwritten to look for the attribute in the format dict values instead of the fmt string.
        """
        return "asctime" in self.fmt_dict.values()

    def formatMessage(self, record) -> dict:
        """
        Overwritten to return a dictionary of the relevant LogRecord attributes instead of a string.
        KeyError is raised if an unknown attribute is provided in the fmt_dict.
        """

        res = {
            fmt_key: record.__dict__[fmt_val]
            for fmt_key, fmt_val in self.fmt_dict.items()
        }

        try:
            res["message"] = ast.literal_eval(res["message"])
            res["message_type"] = "json"
        except Exception:
            res["message_type"] = "str"

        return res

    def format(self, record) -> str:
        """
        Mostly the same as the parent's class method, the difference being that a dict is manipulated and dumped as JSON
        instead of a string.
        """
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        if record.exc_info and (not record.exc_text):
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            message_dict["exc_info"] = record.exc_text

        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict, default=str)


json_formatter = JsonFormatter(
    {
        "level": "levelname",
        "timestamp": "asctime",
        "message": "message",
        "loggerName": "name",
        "processName": "processName",
        # "thread" : "thread",
        "threadName": "threadName",
        # "taskName" : "taskName",
    }
)

if LOG_FORMAT == "json":
    logging.getLogger().handlers.clear()
    logging.basicConfig(stream=sys.stdout, encoding="utf-8")
    logger = logging.getLogger(name=LOG_APP_NAME)
    logger.propagate = False
    sh = logging.StreamHandler()
    sh.setFormatter(json_formatter)

    logger.addHandler(sh)
else:
    logger = logging.getLogger(name=LOG_APP_NAME)
    logging.basicConfig(format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")

logger.setLevel(level=LOG_LEVEL)

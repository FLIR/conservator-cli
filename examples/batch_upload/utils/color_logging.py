import logging

class CustomFormatter(logging.Formatter):
    grey     = "\x1b[38;1m"
    yellow   = "\x1b[33;1m"
    red      = "\x1b[31;1m"
    bold_red = "\x1b[31;1m"
    reset    = "\x1b[0m"
    format_issue  = "%(asctime)s | %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    format_normal = "%(asctime)s | %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_normal + reset,
        logging.INFO: grey + format_normal + reset,
        logging.WARNING: yellow + format_issue + reset,
        logging.ERROR: red + format_issue + reset,
        logging.CRITICAL: bold_red + format_issue + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%H:%M:%S")
        return formatter.format(record)

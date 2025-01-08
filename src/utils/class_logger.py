import logging
import os
import datetime


class Logger:
    """
    Base class for logging functionality.
    """

    def __init__(self, bookmaker: str, debug: bool = False, datetime_format: str = "%Y-%m-%d %H:%M:%S"):
        """
        Initialize the Logger class.

        :param debug: Enables debug logging if True.
        :param datetime_format: Format for datetime in logs.
        """
        self.bookmaker = bookmaker
        self.debug = debug
        self.datetime_format = datetime_format

    def debug_log(self, message: str):
        """
        Logs debug messages if debugging is enabled.

        :param message: The debug message to log.
        """
        if self.debug:
            print(f"[DEBUG] {self._get_datetime()} - {self.bookmaker.upper()} - {message}")

    def info_log(self, message: str):
        """
        Logs informational messages.

        :param message: The informational message to log.
        """
        print(f"[INFO] {self._get_datetime()} - {self.bookmaker.upper()} - {message}")

    def error_log(self, message: str):
        """
        Logs error messages.

        :param message: The error message to log.
        """
        print(f"[ERROR] {self._get_datetime()} - {self.bookmaker.upper()} - {message}")

    def _get_datetime(self) -> str:
        """
        Returns the current datetime as a formatted string.
        """
        return datetime.datetime.now().strftime(self.datetime_format)


def setup_logger(log_file: str = "logs/arbitrage_analysis.log"):
    """
    Sets up the logger configuration for the project.
    :param log_file: Path to the log file.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)  # Create the logs directory if it doesn't exist

    logging.basicConfig(
        level=logging.INFO,  # Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s [%(levelname)s]: %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode='a'),  # Append logs to file
            logging.StreamHandler()  # Print logs to the console
        ]
    )
    # logger.propagate = False
    return logging.getLogger("ArbitrageAnalysis")

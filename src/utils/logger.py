import logging
import os


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
    return logging.getLogger("ArbitrageAnalysis")

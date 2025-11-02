import pandas as pd
import logging
from .loading import read_data, read_process_line
from .indexing import re_indexing
from .telemetry_eng import telemetry_eng
from .summary_eng import summary_eng

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def data_pipeline() -> pd.DataFrame:
    """
    Complete data pipeline:
        - load data
        - filter for Melbourne laps
        - slice track coordinates
        - re-index the data
        - enforce track limits
        - remove laps with insufficient data
    """
    telemetry = read_data()
    line = read_process_line()
    logger.info("Data loaded.")

    telemetry = re_indexing(telemetry)
    logger.info("Data re-indexed")

    telemetry = telemetry_eng(telemetry, line)
    logger.info("Telemetry engineering complete.")

    summary = summary_eng(telemetry)
    logger.info("Summary Engineering complete.")

    logger.info("Pipeline Complete.... Happy Exploring :-)")
    return telemetry, summary

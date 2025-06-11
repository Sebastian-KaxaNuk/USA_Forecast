"""
Dataclass encapsulating the user's selected configuration
"""

from src.usa_forecast.exceptions import ConfigurationError
import datetime
import dataclasses
import numbers

CONFIGURATION_LOGGER_LEVELS = {
    'debug': 'DEBUG',
    'info': 'INFO',
    'warning': 'WARNING',
    'error': 'ERROR',
    'critical': 'CRITICAL'
}


@dataclasses.dataclass(frozen=True, slots=True)
class Configuration:
    start_date: datetime.date
    end_date: datetime.date
    fmp_api_key: str
    tickers: tuple[str, ...]
    window_shift: tuple[int, ...]

    def __post_init__(self):

        if (
            not isinstance(self.start_date, datetime.date)
            or isinstance(self.start_date, datetime.datetime)
        ):
            raise ConfigurationError("Incorrect Configuration.start_date type, expecting datetime.date")

        if (
            not isinstance(self.end_date, datetime.date)
            or isinstance(self.end_date, datetime.datetime)
        ):
            raise ConfigurationError("Incorrect Configuration.end_date type, expecting datetime.date")

        if (
            not isinstance(self.fmp_api_key, str)

        ):
            raise ConfigurationError("Incorrect Configuration.fmp_api_key type, expecting a str")

        if any(ticker is None or not isinstance(ticker, str) for ticker in self.tickers):
            msg = "Null or non-string value found in Configuration.tickers."
            raise ConfigurationError(msg)

        if any(shift is None or not isinstance(shift, int) or shift <= 0 for shift in self.window_shift):
            msg = "All values in Configuration.window_shift must be positive integers."
            raise ConfigurationError(msg)

        # if any(shift is None or not isinstance(shift, numbers.Integral) or shift <= 0 for shift in self.window_shift):
        #     raise ConfigurationError("All values in Configuration.window_shift must be positive integers.")

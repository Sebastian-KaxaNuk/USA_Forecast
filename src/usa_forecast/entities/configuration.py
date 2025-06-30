from usa_forecast.exceptions import ConfigurationError
import datetime
import dataclasses


VALID_SUMMARY_MODES = {"latest", "daily", "frequency", "custom"}
VALID_SUMMARY_FREQUENCIES = {"weekly", "monthly", "quarterly", "semiannual", "annual"}

@dataclasses.dataclass(frozen=True, slots=True)
class Configuration:
    """
    Dataclass encapsulating the user's selected configuration.
    """
    start_date: datetime.date
    end_date: datetime.date
    fmp_api_key: str
    tickers: tuple[str, ...]
    window_shift: tuple[int, ...]
    stay_update: str
    summary_mode: str
    summary_frequency: str
    summary_start_date: datetime.date
    summary_end_date: datetime.date

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

        if not isinstance(self.fmp_api_key, str):
            raise ConfigurationError("Incorrect Configuration.fmp_api_key type, expecting a str")

        if any(ticker is None or not isinstance(ticker, str) for ticker in self.tickers):
            raise ConfigurationError("Null or non-string value found in Configuration.tickers.")

        if any(shift is None or not isinstance(shift, int) or shift <= 0 for shift in self.window_shift):
            raise ConfigurationError("All values in Configuration.window_shift must be positive integers.")

        if not isinstance(self.stay_update, str) or self.stay_update not in {"True", "False"}:
            raise ConfigurationError("Incorrect Configuration.stay_update: expecting a string 'True' or 'False'")

        if (
            not isinstance(self.summary_start_date, datetime.date)
            or isinstance(self.summary_start_date, datetime.datetime)
        ):
            raise ConfigurationError("Incorrect Configuration.summary_start_date type, expecting datetime.date")

        if (
            not isinstance(self.summary_end_date, datetime.date)
            or isinstance(self.summary_end_date, datetime.datetime)
        ):
            raise ConfigurationError("Incorrect Configuration.summary_end_date type, expecting datetime.date")

        if not isinstance(self.summary_frequency, str) or self.summary_frequency.lower() not in VALID_SUMMARY_FREQUENCIES:
            raise ConfigurationError(
                f"Invalid Configuration.summary_frequency. Expected one of: {', '.join(VALID_SUMMARY_FREQUENCIES)}"
            )

        if not isinstance(self.summary_mode, str) or self.summary_mode.lower() not in VALID_SUMMARY_MODES:
            raise ConfigurationError(
                f"Invalid Configuration.summary_mode. Expected one of: {', '.join(VALID_SUMMARY_MODES)}"
            )

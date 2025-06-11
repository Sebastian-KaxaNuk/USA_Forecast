class PortfolioValidationError(Exception):
    """
    Raised when the portfolio structure or content is invalid.
    Typically used during validation of portfolio weights,
    dates, or ticker formats inside the PortfolioEntity.
    """
    pass

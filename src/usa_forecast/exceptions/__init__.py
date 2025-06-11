class ExplanatoryDataAnalysisError(Exception):
    pass


class ConfigurationError(ExplanatoryDataAnalysisError):
    pass


class InjectedDependencyError(ExplanatoryDataAnalysisError):
    pass


class MissingCSVReadError(ExplanatoryDataAnalysisError):
    pass

class ConfigurationError(Exception):
    pass

class ConfigurationHandlerError(Exception):
    pass

"""
Interface for classes creating Configuration entities and related dependencies.
"""

from usa_forecast.entities.configuration import Configuration

import abc

class ConfiguratorInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_configuration(self) -> Configuration:
        ...


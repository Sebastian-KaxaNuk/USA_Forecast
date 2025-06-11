"""
Interface for classes creating Configuration entities and related dependencies.
"""

from src.usa_forecast.entities.configuration import Configuration

import abc
import logging
import types


class ConfiguratorInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_configuration(self) -> Configuration:
        ...


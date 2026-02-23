import logging

from abc import ABC, abstractmethod
from typing import Any

from app.calculation import Calculation

class HistoryObserver(ABC):

    '''
    Abstract base class for calculator observers
    '''

    @abstractmethod
    def update(self, calculation: Calculation) -> None:

        # Handle new calculation event

        pass # pragma: no cover

class LoggingObserver(HistoryObserver):

    '''
    Logs calculations into a file
    '''

    def update(self, calculation: Calculation) -> None:

        if calculation is None:
            raise AttributeError('Calculation cannot be None')

        logging.info(
            f'Calculation performed: {calculation.operation} '
            f'({calculation.operand1}, {calculation.operand2}) = '
            f'{calculation.result}'
        )

class AutoSaveObserver(HistoryObserver):

    '''
    Logs history into a file automatically after each operation, if auto-save is on
    '''

    def __init__(self, calculator: Any):

        # Save calculator config and validate it has the required attributes

        if not hasattr(calculator, 'config') or not hasattr(calculator, 'save_history'):
            raise TypeError("Calculator must have 'config' and 'save_history' attributes")

        self.calculator = calculator

    def update(self, calculation: Calculation) -> None:

        if calculation is None:
            raise AttributeError('Calculation cannot be None')

        if self.calculator.config.auto_save:
            self.calculator.save_history()
            logging.info('History auto-saved')

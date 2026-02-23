import pytest

from unittest.mock import Mock, patch

from app.calculation import Calculation
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.history import AutoSaveObserver, LoggingObserver

@patch('logging.info')
def test_logging_observer_logs_calculation(log_mock):

    # Test simple logging of a calculation

    calc_mock = Mock(spec=Calculation)
    calc_mock.operation = 'addition'
    calc_mock.operand1 = 5
    calc_mock.operand2 = 3
    calc_mock.result = 8

    observer = LoggingObserver()
    observer.update(calc_mock)
    log_mock.assert_called_once_with('Calculation performed: addition (5, 3) = 8')

def test_logging_observer_no_calc():

    # Make sure there is an error if a calc is not passed to the update

    observer = LoggingObserver()
    with pytest.raises(AttributeError):
        observer.update(None)

def test_autosave_observer_triggers_save():

    # Verify any updates trigger the save

    calc_mock = Mock(spec=Calculator)
    calc_mock.config = Mock(spec=CalculatorConfig)
    calc_mock.config.auto_save = True
    observer = AutoSaveObserver(calc_mock)
    observer.update(calc_mock)
    calc_mock.save_history.assert_called_once()

# Additional test cases

def test_autosave_observer_invalid_calculator():

    with pytest.raises(TypeError, match="Calculator must have 'config' and 'save_history' attributes"):
        AutoSaveObserver(None)

def test_autosave_observer_no_calc():

    # Make sure there is an error if a calc is not passed to the update

    calc_mock = Mock(spec=Calculator)
    calc_mock.config = Mock(spec=CalculatorConfig)
    calc_mock.config.auto_save = True
    observer = AutoSaveObserver(calc_mock)

    with pytest.raises(AttributeError):
        observer.update(None)

def test_autosave_observer_no_autosave():

    # Verify any updates trigger the save

    calc_mock = Mock(spec=Calculator)
    calc_mock.config = Mock(spec=CalculatorConfig)
    calc_mock.config.auto_save = False
    observer = AutoSaveObserver(calc_mock)
    observer.update(calc_mock)
    calc_mock.save_history.assert_not_called()

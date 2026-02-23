import datetime
import pandas as pd
import pytest

from decimal import Decimal
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch, PropertyMock

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError
from app.exceptions import ValidationError
from app.history import LoggingObserver
from app.input_validators import InputValidator
from app.operations import OperationFactory

@pytest.fixture
def calculator():

    # Create a temporary directory file paths

    with TemporaryDirectory() as temp_dir:

        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:

            mock_log_dir.return_value = temp_path / 'logs'
            mock_log_file.return_value = temp_path / 'logs/calculator.log'
            mock_history_dir.return_value = temp_path / 'history'
            mock_history_file.return_value = temp_path  / 'history/calculator_history.csv'

            yield Calculator(config=config)

def test_calculator_init(calculator):

    # Check calculation var initialization

    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

@patch('app.calculator.logging.info')
def test_logging_setup(log_mock):

    # Check log paths

    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:

        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')

        Calculator(CalculatorConfig())
        log_mock.assert_any_call('Calculator initialized with configuration')

def test_add_observer(calculator):

    # Test adding an observer

    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers

def test_remove_observer(calculator):

    # Test removing an observer

    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

def test_set_operation(calculator):

    # Set a calc operation
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

def test_perform_operation_addition(calculator):

    # Do an addition operation

    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')

def test_perform_operation_validation_error(calculator):

    # Test an invalid operation

    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)

def test_perform_operation_operation_error(calculator):

    # Test n invalid operation

    with pytest.raises(OperationError, match='No operation set'):
        calculator.perform_operation(2, 3)

def test_undo(calculator):

    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []

def test_redo(calculator):

    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):

    # Test that history was saved to csv

    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):

    # Load history from csv

    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })

    calculator.load_history()
    assert len(calculator.history) == 1
    assert calculator.history[0].operation == 'Addition'
    assert calculator.history[0].operand1 == Decimal('2')
    assert calculator.history[0].operand2 == Decimal('3')
    assert calculator.history[0].result == Decimal('5')

def test_clear_history(calculator):

    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

# Additional cases beyond ones in instructor example

@patch('app.calculator.logging.warning')
def test_calculator_fail_history_load(log_mock, monkeypatch):

    # Simulate error in loading history

    def bad_load_history(self):
        raise ValueError('Force fail')

    monkeypatch.setattr(Calculator, 'load_history', bad_load_history)
    Calculator()
    log_mock.assert_any_call('Could not load existing history: Force fail')

def test_calculator_fail_setup_logging(monkeypatch):

    # Simulate error in setting up logging

    monkeypatch.setattr(CalculatorConfig, 'log_file', None)
    with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'resolve'"):
        Calculator()

def test_calculator_history_too_big(calculator):

    # Perform more operations than the history size (default of 1000)

    for i in range(1001):
        operation = OperationFactory.create_operation('add')
        calculator.set_operation(operation)
        calculator.perform_operation(2, i)

def test_calculator_fail_operation(monkeypatch, calculator):

    # Simulate error in perform_operation

    def bad_validate_number(value, config):
        raise ValueError('Force fail')

    monkeypatch.setattr(InputValidator, 'validate_number', bad_validate_number)
    with pytest.raises(Exception, match='Operation failed: Force fail'):
        operation = OperationFactory.create_operation('add')
        calculator.set_operation(operation)
        calculator.perform_operation(2, 0)

def test_fail_save_history(monkeypatch):

    # Simulate error in save_history

    def bad_to_csv(*args, **kwargs):
        raise ValueError('forced csv failure')

    monkeypatch.setattr('pandas.DataFrame.to_csv', bad_to_csv)

    with pytest.raises(Exception, match='Failed to save history: forced csv failure'):
        Calculator().save_history()

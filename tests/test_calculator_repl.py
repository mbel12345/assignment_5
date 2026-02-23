import pytest

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, PropertyMock

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_repl import calculator_repl
from app.exceptions import OperationError

@pytest.fixture
def calculator():

    # Create a temporary directory file paths

    with TemporaryDirectory() as temp_dir:

        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path, auto_save=True)

        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:

            mock_log_dir.return_value = temp_path / 'logs'
            mock_log_file.return_value = temp_path / 'logs/calculator.log'
            mock_history_dir.return_value = temp_path / 'history'
            mock_history_file.return_value = temp_path  / 'history/calculator_history.csv'

            calc = Calculator(config=config)
            calc.clear_history()
            with open(calculator.config.history_file, 'w') as out_f:
                out_f.write('')

            yield calc


@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_repl_exit(mock_print, mock_input):

    # Test REPL Exit

    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call('History saved successfully')
        mock_print.assert_any_call('Goodbye!')

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_repl_help(mock_print, mock_input):

    # Test REPL Help

    calculator_repl()
    mock_print.assert_any_call('\nAvailable commands:')

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_repl_addition(mock_print, mock_input):

    # Test REPL Addtion
    calculator_repl()
    mock_print.assert_any_call('\nResult: 5')

# Additonal tests, beyond the instructor example

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_repl_fail_save_history(mock_print, mock_input, monkeypatch):

    # Simulate error in perform_operation

    def bad_save_history(self):
        raise ValueError('Force fail')

    monkeypatch.setattr(Calculator, 'save_history', bad_save_history)
    calculator_repl()
    mock_print.assert_any_call('Calculator started. Type \'help\' for commands')
    mock_print.assert_any_call('Warning: Could not save history: Force fail')

@patch('builtins.input', side_effect=['clear', 'add', '3', '4', 'subtract', '6', '2', 'history', 'exit'])
@patch('builtins.print')
def test_repl_history_with_data(mock_print, mock_input):

    # Show history after performing operations

    calculator_repl()
    mock_print.assert_any_call('1. Addition(3, 4) = 7')
    mock_print.assert_any_call('2. Subtraction(6, 2) = 4')

@patch('builtins.input', side_effect=['clear', 'history', 'exit'])
@patch('builtins.print')
def test_repl_history_empty(mock_print, mock_input):

    # Show history with no data

    calculator_repl()
    mock_print.assert_any_call('No calculations in history')

@patch('builtins.input', side_effect=['clear', 'add', '3', '6', 'undo', 'exit'])
@patch('builtins.print')
def test_repl_undo_with_data(mock_print, mock_input, monkeypatch):

    # Do undo with data

    calculator_repl()
    mock_print.assert_any_call('Operation undone')

@patch('builtins.input', side_effect=['clear', 'undo', 'exit'])
@patch('builtins.print')
def test_repl_undo_empty(mock_print, mock_input, monkeypatch):

    # Do undo when there is no history

    calculator_repl()
    mock_print.assert_any_call('Nothing to undo')

@patch('builtins.input', side_effect=['clear', 'add', '3', '6', 'undo', 'redo', 'exit'])
@patch('builtins.print')
def test_repl_redo_with_data(mock_print, mock_input, monkeypatch):

    # Do redo with data

    calculator_repl()
    mock_print.assert_any_call('Operation redone')

@patch('builtins.input', side_effect=['clear', 'redo', 'exit'])
@patch('builtins.print')
def test_repl_redo_empty(mock_print, mock_input, monkeypatch):

    # Do redo when there is no history

    calculator_repl()
    mock_print.assert_any_call('Nothing to redo')

@patch('builtins.input', side_effect=['clear', 'add', '3', '6', 'save', 'exit'])
@patch('builtins.print')
def test_repl_save(mock_print, mock_input, monkeypatch):

    # Do redo with data

    calculator_repl()
    mock_print.assert_any_call('History saved successfully')


@patch('builtins.input', side_effect=['clear', 'save', 'exit'])
@patch('builtins.print')
def test_repl_fail_save(mock_print, mock_input, monkeypatch):

    # Simulate error in save

    def bad_save(self):
        raise ValueError('Force fail')

    monkeypatch.setattr(Calculator, 'save_history', bad_save)
    calculator_repl()
    mock_print.assert_any_call('Error saving history: Force fail')

@patch('builtins.input', side_effect=['clear', 'load', 'exit'])
@patch('builtins.print')
def test_repl_load(mock_print, mock_input, monkeypatch):

    # Do redo with load

    calculator_repl()
    mock_print.assert_any_call('History loaded successfully')

@patch('builtins.input', side_effect=['clear', 'load', 'exit'])
@patch('builtins.print')
def test_repl_fail_load(mock_print, mock_input, monkeypatch):

    # Simulate error in load

    def bad_load(self):
        raise ValueError('Force fail')

    monkeypatch.setattr(Calculator, 'load_history', bad_load)
    calculator_repl()
    mock_print.assert_any_call('Error loading history: Force fail')

@patch('builtins.input', side_effect=['clear', 'add', 'cancel', 'exit'])
@patch('builtins.print')
def test_repl_cancel_first(mock_print, mock_input, monkeypatch):

    # Do cancel with first number

    calculator_repl()
    mock_print.assert_any_call('Operation cancelled')

@patch('builtins.input', side_effect=['clear', 'add', '3', 'cancel', 'exit'])
@patch('builtins.print')
def test_repl_cancel_second(mock_print, mock_input, monkeypatch):

    # Do cancel with second number

    calculator_repl()
    mock_print.assert_any_call('Operation cancelled')

@patch('builtins.input', side_effect=['clear', 'add', '3.5', '2.1', 'exit'])
@patch('builtins.print')
def test_repli_normalize_decimal(mock_print, mock_input, monkeypatch):

    # Do cancel with second number

    calculator_repl()

@patch('builtins.input', side_effect=['clear', 'add', '3', '4', 'exit'])
@patch('builtins.print')
def test_replic_invalid_operation(mock_print, mock_input, monkeypatch):

    # Simulate OperationError

    def bad_operation(self, a, b):
        raise OperationError('Force fail')

    monkeypatch.setattr(Calculator, 'perform_operation', bad_operation)
    calculator_repl()
    mock_print.assert_any_call('Error: Force fail')

@patch('builtins.input', side_effect=['clear', 'add', '3', '4', 'exit'])
@patch('builtins.print')
def test_repl_unexpected_operation_error(mock_print, mock_input, monkeypatch):

    # Simulate unexpected error during operation

    def bad_operation(self, a, b):
        raise ValueError('Force fail')

    monkeypatch.setattr(Calculator, 'perform_operation', bad_operation)
    calculator_repl()
    mock_print.assert_any_call('Unexpected error: Force fail')

@patch('builtins.input', side_effect=['clear', 'my_opp', 'exit'])
@patch('builtins.print')
def test_repl_unknown_operation(mock_print, mock_input):

    # Test unsupported operation

    calculator_repl()
    mock_print.assert_any_call("Unknown command: 'my_opp'. Type 'help' for available commands.")

@patch('builtins.input', side_effect=['clear', 'exit'])
@patch('builtins.print')
def test_repl_top_level_error(mock_print, mock_input, monkeypatch):

    # Test top-level error

    def bad_add_observer(self, observer):
        raise ValueError('Force fail')

    monkeypatch.setattr(Calculator, 'add_observer', bad_add_observer)
    calculator_repl()
    mock_print.assert_any_call('Fatal error: Force fail')

# Force input to fail
class FakeInput1(str):
    def lower(self):
        raise ValueError('Force fail')

@patch('builtins.input', side_effect=[FakeInput1('add'), 'exit'])
@patch('builtins.print')
def test_repl_second_level_error(mock_print, mock_input):

    # Test second-level error

    calculator_repl()
    mock_print.assert_any_call('Error: Force fail')

# Force input to fail
class FakeInput2(str):
    def lower(self):
        raise KeyboardInterrupt('Force fail')

@patch('builtins.input', side_effect=[FakeInput2('add'), 'exit'])
@patch('builtins.print')
def test_repl_keyboard_interrupt(mock_print, mock_input):

    # Test Keyboard Interrupt

    calculator_repl()
    mock_print.assert_any_call('\nOperation cancelled')

# Force input to fail
class FakeInput3(str):
    def lower(self):
        raise EOFError('Force fail')

@patch('builtins.input', side_effect=[FakeInput3('add'), 'exit'])
@patch('builtins.print')
def test_repl_eof_error(mock_print, mock_input):

    # Test EOF Error

    calculator_repl()
    mock_print.assert_any_call('\nInput terminated. Exiting...')

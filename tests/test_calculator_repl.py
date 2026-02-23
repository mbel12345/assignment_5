from unittest.mock import patch

from app.calculator_repl import calculator_repl

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):

    # Test REPL Exit

    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call('History saved successfully')
        mock_print.assert_any_call('Goodbye!')

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):

    # Test REPL Help

    calculator_repl()
    mock_print.assert_any_call('\nAvailable commands:')

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):

    # Test REPL Addtion
    calculator_repl()
    mock_print.assert_any_call('\nResult: 5')

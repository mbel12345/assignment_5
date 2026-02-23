import logging
import pytest
import re

from datetime import datetime
from decimal import Decimal, InvalidOperation

from app.calculation import Calculation
from app.exceptions import OperationError

def test_addition():

    # Test Add calculation

    calc = Calculation(operation='Addition', operand1=Decimal('2'), operand2=Decimal('3'))
    assert calc.result == Decimal('5')

def test_subtraction():

    # Test Subtract calculation

    calc = Calculation(operation='Subtraction', operand1=Decimal('5'), operand2=Decimal('3'))
    assert calc.result == Decimal('2')

def test_multiplication():

    # Test Multiply calculation

    calc = Calculation(operation='Multiplication', operand1=Decimal('4'), operand2=Decimal('2'))
    assert calc.result == Decimal('8')

def test_division():

    # Test Divide calculation

    calc = Calculation(operation='Division', operand1=Decimal('8'), operand2=Decimal('2'))
    assert calc.result == Decimal('4')

def test_division_by_zero():

    # Check for division by zero error

    with pytest.raises(OperationError, match='Division by zero is not allowed'):
        Calculation(operation='Division', operand1=Decimal('8'), operand2=Decimal('0'))

def test_power():

    # Test Power calculation

    calc = Calculation(operation='Power', operand1=Decimal('2'), operand2=Decimal('3'))
    assert calc.result == Decimal('8')

def test_negative_power():

    # Check for error when trying to raise to a negative power

    with pytest.raises(OperationError, match='Negative exponents are not supported'):
        Calculation(operation='Power', operand1=Decimal('2'), operand2=Decimal('-3'))

def test_root():

    # Test Root calculation

    calc = Calculation(operation='Root', operand1=Decimal('16'), operand2=Decimal('2'))
    assert calc.result == Decimal('4')

def test_negative_root():

    # Check for error when trying to compute root of a negative number

    with pytest.raises(OperationError, match='Cannot calculate root of negative number'):
        Calculation(operation='Root', operand1=Decimal('-16'), operand2=Decimal('2'))

def test_zero_root():

    # Check for error when trying to compute the 0th root of a number

    with pytest.raises(OperationError, match='Zero root is undefined'):
        Calculation(operation='Root', operand1=Decimal('3'), operand2=Decimal('0'))

def test_unknown_operation():

    # Check for unknown operation error

    with pytest.raises(OperationError, match='Unknown operation'):
        Calculation(operation='Unknown', operand1=Decimal('5'), operand2=Decimal('3'))

def test_to_dict():

    # Test converting a Calculator to dict

    calc = Calculation(operation='Addition', operand1=Decimal('2'), operand2=Decimal('3'))
    result_dict = calc.to_dict()
    assert result_dict == {
        'operation': 'Addition',
        'operand1': '2',
        'operand2': '3',
        'result': '5',
        'timestamp': calc.timestamp.isoformat(),
    }

def test_from_dict():

    # Test loading a Calculator from dict

    data = {
        'operation': 'Addition',
        'operand1': '2',
        'operand2': '3',
        'result': '5',
        'timestamp': datetime.now().isoformat()
    }

    calc = Calculation.from_dict(data)
    assert calc.operation == 'Addition'
    assert calc.operand1 == Decimal('2')
    assert calc.operand2 == Decimal('3')
    assert calc.result == Decimal('5')

def test_invalid_from_dict():

    # Test failure to load a Calculator from dict

    data = {
        'operation': 'Addition',
        'operand1': 'invalid',
        'operand2': '3',
        'result': '5',
        'timestamp': datetime.now().isoformat(),
    }

    with pytest.raises(OperationError, match='Invalid calculation data'):
        Calculation.from_dict(data)

def test_format_result():

    # Test using the right precision in decimal numbers

    calc = Calculation(operation='Division', operand1=Decimal('1'), operand2=Decimal('3'))
    assert calc.format_result(precision=2) == '0.33'
    assert calc.format_result(precision=10) == '0.3333333333'

def test_equality():

    # Test comparison between Calculators

    calc_1 = Calculation(operation='Addition', operand1=Decimal('2'), operand2=Decimal('3'))
    calc_2 = Calculation(operation='Addition', operand1=Decimal('2'), operand2=Decimal('3'))
    calc_3 = Calculation(operation='Subtraction', operand1=Decimal('5'), operand2=Decimal('3'))

    assert calc_1 == calc_2
    assert calc_1 != calc_3

def test_from_dict_result_mismatch(caplog):

    # Check logging warning

    data = {
        'operation': 'Addition',
        'operand1': '2',
        'operand2': '3',
        'result': '10',
        'timestamp': datetime.now().isoformat(),
    }

    with caplog.at_level(logging.WARNING):
        Calculation.from_dict(data)

    assert 'Loaded calculation result 10 differs from computed result 5' in caplog.text

'''
Cases beyond the instructor-posted code, to ensure full coverage
'''

def test_calculate_arithmetic_error(monkeypatch):

    # Test unexpected Arithmetic error

    class BadDecimal(Decimal):
        def __truediv__(self, other):
            raise ArithmeticError('force failure')

    import app.calculation as calc_mod
    monkeypatch.setattr(calc_mod, 'Decimal', BadDecimal)

    with pytest.raises(OperationError, match='Calculation failed: force failure'):
        Calculation(operation='Division', operand1=BadDecimal('5'), operand2=BadDecimal('2'))

def test_calculation_str():

    # Test __str__ method

    calc = Calculation(operation='Addition', operand1=Decimal('4'), operand2=Decimal('2'))
    assert str(calc) == 'Addition(4, 2) = 6'

def test_calculation_repr():

    # Test __repr__ method

    calc = Calculation(operation='Addition', operand1=Decimal('3'), operand2=Decimal('2'))
    assert re.match("Calculation\\(operation='Addition', operand1=3, operand2=2, result=5, timestamp=.*\\)", repr(calc))

def test_equals_wrong_types():

    # Check that an error is thrown in __eq__ when comparing a Calculation to a non-Calculation

    calc = Calculation(operation='Addition', operand1=Decimal('0'), operand2=Decimal('0'))
    assert calc.__eq__(0) == NotImplemented

def test_format_result_error(monkeypatch):

    # Test error during formatting

    class BadResult:

        def __init__(self, x):

            self.x = x

        def __str__(self):

            return str(self.x)

        def normalize(self):
            raise InvalidOperation('force formatting failure')

    calc = Calculation(operation='Addition', operand1=Decimal('5'), operand2=Decimal('2'))
    calc.result = BadResult('34')
    assert calc.format_result() == '34'


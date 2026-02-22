import pytest

from decimal import Decimal

from app.exceptions import ValidationError
from app.operations import Addition
from app.operations import Division
from app.operations import Multiplication
from app.operations import Operation
from app.operations import OperationFactory
from app.operations import Power
from app.operations import Root
from app.operations import Subtraction

class TestOperation:

    '''
    Test the base Operation class.
    '''

    def test_str_representation(self):

        # Test that str returns the class name.

        class TestOp(Operation):
            def execute(self, a: Decimal, b: Decimal) -> Decimal:
                return a
            def validate_operands(self, a: Decimal, b: Decimal) -> None:
                pass

        assert str(TestOp()) == 'TestOp'

class BaseOperationTest:

    '''
    Use this class to facilitate paramterized testing, instead of the lengthy pytest.mark.parametrize.
    This also means testing will be standardized across different sub-classes.
    '''

    def test_valid_operations(self):

        # Test operation with valid inputs

        operation = self.operation_class()
        for name, case in self.valid_test_cases.items():
            a = Decimal(str(case['a']))
            b = Decimal(str(case['b']))
            expected = Decimal(str(case['expected']))
            result = operation.execute(a, b)
            assert result == expected, f'Failed case: {name}'

    def test_invalid_operations(self):

        # Test operation with invalid inputs, and verify the correct errors were raised.

        operation = self.operation_class()
        for name, case in self.invalid_test_cases.items():
            a = Decimal(str(case['a']))
            b = Decimal(str(case['b']))
            expected_error = case['error']
            expected_message = case['message']
            with pytest.raises(expected_error, match=expected_message):
                operation.execute(a, b)

class TestAddition(BaseOperationTest):

    '''
    Test Addition operation
    '''

    operation_class = Addition
    valid_test_cases = {
        'positive_numbers': {'a': '5', 'b': '3', 'expected': '8'},
        'negative_numbers': {'a': '-5', 'b': '-3', 'expected': '-8'},
        'mixed_signs': {'a': '-5', 'b': '3', 'expected': '-2'},
        'zero_sum': {'a': '5', 'b': '-5', 'expected': '0'},
        'decimals': {'a': '5.5', 'b': '3.3', 'expected': '8.8'},
        'large_numbers': {'a': '1e10', 'b': '1e10', 'expected': '20000000000'},
    }
    invalid_test_cases = {}

class TestSubtraction(BaseOperationTest):

    '''
    Test Subtraction operation
    '''

    operation_class = Subtraction
    valid_test_cases = {
        'positive_numbers': {'a': '5', 'b': '3', 'expected': '2'},
        'negative_numbers': {'a': '-5', 'b': '-3', 'expected': '-2'},
        'mixed_signs': {'a': '-5', 'b': '3', 'expected': '-8'},
        'zero_result': {'a': '5', 'b': '5', 'expected': '0'},
        'decimals': {'a': '5.5', 'b': '3.3', 'expected': '2.2'},
        'large_numbers': {'a': '1e10', 'b': '1e9', 'expected': '9000000000'},
    }
    invalid_test_cases = {}

class TestMultiplication(BaseOperationTest):

    '''
    Test Multiplication operation
    '''

    operation_class = Multiplication
    valid_test_cases = {
        'positive_numbers': {'a': '5', 'b': '3', 'expected': '15'},
        'negative_numbers': {'a': '-5', 'b': '-3', 'expected': '15'},
        'mixed_signs': {'a': '-5', 'b': '3', 'expected': '-15'},
        'multiply_by_zero': {'a': '5', 'b': '0', 'expected': '0'},
        'decimals': {'a': '5.5', 'b': '3.3', 'expected': '18.15'},
        'large_numbers': {'a': '1e5', 'b': '1e5', 'expected': '10000000000'},
    }
    invalid_test_cases = {}

class TestDivision(BaseOperationTest):

    '''
    Test Division operation
    '''

    operation_class = Division
    valid_test_cases = {
        'positive_numbers': {'a': '6', 'b': '2', 'expected': '3'},
        'negative_numbers': {'a': '-6', 'b': '-2', 'expected': '3'},
        'mixed_signs': {'a': '-6', 'b': '2', 'expected': '-3'},
        'decimals': {'a': '5.5', 'b': '2', 'expected': '2.75'},
        'divide_zero': {'a': '0', 'b': '5', 'expected': '0'},
    }
    invalid_test_cases = {
        'divide_by_zero': {'a': '5', 'b': '0', 'error': ValidationError, 'message': 'Division by zero is not allowed'},
    }

class TestPower(BaseOperationTest):

    '''
    Test Power operation
    '''

    operation_class = Power
    valid_test_cases = {
        'positive_base_and_exponent': {'a': '2', 'b': '3', 'expected': '8'},
        'zero_exponent': {'a': '5', 'b': '0', 'expected': '1'},
        'one_exponent': {'a': '5', 'b': '1', 'expected': '5'},
        'decimal_base': {'a': '2.5', 'b': '2', 'expected': '6.25'},
        'zero_base': {'a': '0', 'b': '5', 'expected': '0'},
    }
    invalid_test_cases = {
        'negative_exponent': {'a': '2', 'b': '-3', 'error': ValidationError, 'message': 'Negative exponents not supported'},
    }

class TestRoot(BaseOperationTest):

    '''
    Test Root operation
    '''

    operation_class = Root
    valid_test_cases = {
        'square_root': {'a': '9', 'b': '2', 'expected': '3'},
        'cube_root':  {'a': '27', 'b': '3', 'expected': '3'},
        'fourth_root':  {'a': '16', 'b': '4', 'expected': '2'},
        'decimal_root': {'a': '2.25', 'b': '2', 'expected': '1.5'},
    }
    invalid_test_cases = {
        'negative_base': {'a': '-9', 'b': '2', 'error': ValidationError, 'message': 'Cannot calculate root of negative number'},
        'zero_root': {'a': '9', 'b': '0', 'error': ValidationError, 'message': 'Zero root is undefined'},
    }

class TestOperationFactory:

    '''
    Test OperationFactory functionality
    '''

    def test_create_valid_operations(self):

        # Test creation of all valid operations

        operation_map = {
            'add': Addition,
            'subtract': Subtraction,
            'multiply': Multiplication,
            'divide': Division,
            'power': Power,
            'root': Root,
        }

        for op_name, op_class in operation_map.items():

            # Correct case
            operation = OperationFactory.create_operation(op_name)
            assert isinstance(operation, op_class)

            # Case insensitive
            operation = OperationFactory.create_operation(op_name.upper())
            assert isinstance(operation, op_class)

    def test_create_invalid_operation(self):

        # Test creation of invalid operation

        with pytest.raises(ValueError, match='Unknown operation: invalid_op'):
            OperationFactory.create_operation('invalid_opp')

    def test_register_valid_operation(self):

        # Test registering a new valid operation

        class SomeOperation(Operation):
            def execute(self, a: Decimal, b: Decimal) -> Decimal:
                return a
            def validate_operands(self, a, b):
                pass

        OperationFactory.register_operation('new_op', SomeOperation)
        operation = OperationFactory.create_operation('new_op')
        assert isinstance(operation, SomeOperation)

    def test_register_invalid_operation(self):

        # Test registering an invalid operation, verify an error is raised

        class BadOperation:
            pass

        with pytest.raises(TypeError, match='Operation class must inherit'):
            OperationFactory.register_operation('invalid', BadOperation)

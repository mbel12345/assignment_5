import datetime
import logging

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Dict

from app.exceptions import OperationError

@dataclass
class Calculation:

    '''
    This class encapsulates the details of a mathematical calculation,
    including the operation name, two nubmers, result, and timestamp.
    '''

    operation: str
    operand1: Decimal
    operand2: Decimal
    result: Decimal = field(init=False)
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post_init__(self):

        # Takes place after the default __init__ method for dataclass that initiates all the values

        self.result = self.calculate()

    def calculate(self) -> Decimal:

        # Do the calculation.

        operations = {
            'Addition': lambda x, y: x + y,
            'Subtraction': lambda x, y: x - y,
            'Multiplication': lambda x, y: x * y,
            'Division': lambda x, y: x / y if y != 0 else self._raise_div_zero(),
            'Power': lambda x, y: Decimal(pow(float(x), float(y))) if y >= 0 else self._raise_neg_power(),
            'Root': lambda x, y: Decimal(pow(float(x), 1 / float(y))) if x >= 0 and y != 0 else self._raise_invalid_root(x, y),
        }

        # Get the operation from the dict based on operation name
        op = operations.get(self.operation)
        if not op:
            raise OperationError(f'Unknown operation: {self.operation}')

        try:

            return op(self.operand1, self.operand2)

        except (InvalidOperation, ValueError, ArithmeticError) as e:

            raise OperationError(f'Calculation failed: {str(e)}')

    @staticmethod
    def _raise_div_zero():

        # Raise exception for division by 0

        raise OperationError('Division by zero is not allowed')

    @staticmethod
    def _raise_neg_power():

        # Raise exception when negative exponent is used in power operation

        raise OperationError('Negative exponents are not supported')

    @staticmethod
    def _raise_invalid_root(x: Decimal, y: Decimal):

        # Raise exception if invalid numbers are provided in Root operation

        if y == 0:
            raise OperationError('Zero root is undefined')

        if x < 0:
            raise OperationError('Cannot calculate root of negative number')

        # This function is only called when one of the above conditions is met, so this is dead code that needs pragma: no cover
        return # pragma: no cover

    def to_dict(self) -> Dict[str, Any]:

        # Convert to dict showing most important info like operation and operands

        return {
            'operation': self.operation,
            'operand1': str(self.operand1),
            'operand2': str(self.operand2),
            'result': str(self.result),
            'timestamp': self.timestamp.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Calculation':

        # Create calculation from dictionary

        try:

            calc = Calculation(
                operation=data['operation'],
                operand1=Decimal(data['operand1']),
                operand2=Decimal(data['operand2']),
            )

            calc.timestamp = datetime.datetime.fromisoformat(data['timestamp'])

            saved_result = Decimal(data['result'])
            if calc.result != saved_result:
                logging.warning(
                    f'Loaded calculation result {saved_result} '
                    f'differs from computed result {calc.result}'
                )

            return calc

        except (KeyError, InvalidOperation, ValueError) as e:

            raise OperationError(f'Invalid calculation data: {str(e)}')

    def __str__(self) -> str:

        # Return str representation of the calculation

        return f'{self.operation}({self.operand1}, {self.operand2}) = {self.result}'

    def __repr__(self) -> str:

        # Return detailed str representation of the calculation

        return (
            f"Calculation(operation='{self.operation}', "
            f'operand1={self.operand1}, '
            f'operand2={self.operand2}, '
            f'result={self.result}, '
            f"timestamp='{self.timestamp.isoformat()}')"
        )

    def __eq__(self, other: object) -> bool:

        # Check if two calculations are equal

        if not isinstance(other, Calculation):
            return NotImplemented
        return (
            self.operation == other.operation and
            self.operand1 == other.operand1 and
            self.operand2 == other.operand2 and
            self.result == other.result
        )

    def format_result(self, precision: int = 10) -> str:

        # Format the calculation for the given precision

        try:

            return str(
                self.result.normalize().quantize(
                    Decimal('0.' + '0' * precision)
                ).normalize()
            )

        except InvalidOperation:

            return str(self.result)


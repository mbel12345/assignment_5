from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict

from app.exceptions import ValidationError

class Operation(ABC):

    '''
    Abstract base class for calculator operations. Each operation will inherit from this.
    '''

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:

        # Do the operation on a and b, and return the result.

        pass # pragma: no cover

    @abstractmethod
    def validate_operands(self, a: Decimal, b: Decimal) -> None:

        # Validate the operands, for example that b is not a 0 for the division operation.

        pass # pragma: no cover

    def __str__(self) -> str:

        # Nice string representation of a calculation

        return self.__class__.__name__

class Addition(Operation):

    # Add operation

    def execute(self, a: Decimal, b: Decimal) -> Decimal:

        # Add a and b

        self.validate_operands(a, b)
        return a + b

    def validate_operands(self, a: Decimal, b: Decimal) -> None:

        # Any numbers are valid

        return

class Subtraction(Operation):

    # Subtract operation

    def execute(self, a: Decimal, b: Decimal) -> Decimal:

        # Subtract a and b

        self.validate_operands(a, b)
        return a - b

    def validate_operands(self, a: Decimal, b: Decimal) -> None:

        # Any numbers are valid

        return

class Multiplication(Operation):

    # Multiply operation

    def execute(self, a: Decimal, b: Decimal) -> Decimal:

        # Multiply a and b

        self.validate_operands(a, b)
        return a * b

    def validate_operands(self, a: Decimal, b: Decimal) -> None:

        # Any numbers are valid

        return

class Division(Operation):

    # Divide operation

    def execute(self, a: Decimal, b: Decimal) -> Decimal:

        # Divide a and b

        self.validate_operands(a, b)
        return a / b

    def validate_operands(self, a: Decimal, b: Decimal) -> None:

        # Cannot divide by 0

        if b == 0:
            raise ValidationError('Division by zero is not allowed')

class Power(Operation):

    # Exponent operation

    def execute(self, a: Decimal, b: Decimal) -> Decimal:

        # Compute a raised to b

        self.validate_operands(a, b)
        return a ** b

    def validate_operands(self, a: Decimal, b: Decimal) -> Decimal:

        # Do not support negative exponents (use root instead)
        if b < 0:
            raise ValidationError('Negative exponents not supported')

class Root(Operation):

    # Root operation (inverse of Power)

    def execute(self, a: Decimal, b: Decimal) -> Decimal:

        # Compute a raised to 1/b, for example, use b=2 to find the square root

        self.validate_operands(a, b)
        return a ** (1/b)

    def validate_operands(self, a: Decimal, b: Decimal) -> Decimal:

        # Cannot compute the roots of negative numbers, cannot compute 0 roots

        if a < 0:
            raise ValidationError('Cannot calculate root of negative number')

        if b == 0:
            raise ValidationError('Zero root is undefined')

class OperationFactory:

    # Factory for creation Operations

    _operations: Dict[str, type] = {
        'add': Addition,
        'subtract': Subtraction,
        'multiply': Multiplication,
        'divide': Division,
        'power': Power,
        'root': Root,
    }

    @classmethod
    def register_operation(cls, name: str, operation_class: type) -> None:

        # Register a new operation, i.e. add new entry in _operations to map name to operation_class

        if not issubclass(operation_class, Operation):
            raise TypeError('Operation class must inherit from Operation')

        cls._operations[name.lower()] = operation_class

    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:

        # Return a new instance of an Operation corresponding to operation_type

        operation_class = cls._operations.get(operation_type.lower())

        if not operation_class:
            raise ValueError(f'Unknown operation: {operation_type}')

        return operation_class()

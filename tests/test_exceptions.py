import pytest

from app.exceptions import CalculatorError
from app.exceptions import ConfigurationError
from app.exceptions import OperationError
from app.exceptions import ValidationError

def test_calculate_error_is_base_exception():

    # Test that CalculateError is the base exception

    with pytest.raises(CalculatorError) as e:
        raise CalculatorError('Base calculator error occurred')

    assert str(e.value) == 'Base calculator error occurred'

def test_validation_error_is_calculator_error():

    # Make sure validation error is raised

    with pytest.raises(CalculatorError) as e:
        raise ValidationError('Validation failed')

    assert isinstance(e.value, CalculatorError)
    assert str(e.value) == 'Validation failed'

def test_validation_error_specific_exception():

    # Look for specific error type

    with pytest.raises(ValidationError) as e:
        raise ValidationError('Validation error')

    assert str(e.value) == 'Validation error'

def test_operation_error_is_calculator_error():

    # Test that OperationError is a CalculatorError

    with pytest.raises(CalculatorError) as e:
        raise OperationError('Operation failed')

    assert isinstance(e.value, CalculatorError)
    assert str(e.value) == 'Operation failed'

def test_operation_error_specific_exception():

    # Check the error message

    with pytest.raises(OperationError) as e:
        raise OperationError('Specific error')

    assert str(e.value) == 'Specific error'

def test_configuration_error_is_calculator_error():

    # Check that ConfigurationError is a sub-class of CalculatorError

    with pytest.raises(CalculatorError) as e:
        raise ConfigurationError('Configuration invalid')

    assert isinstance(e.value, CalculatorError)
    assert str(e.value) == 'Configuration invalid'

def test_configuration_error_specific_exception():

    # Check the error message

    with pytest.raises(ConfigurationError) as e:
        raise ConfigurationError('Specific error')

    assert str(e.value) == 'Specific error'

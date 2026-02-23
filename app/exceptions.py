class CalculatorError(Exception):

    '''
    Base class for all other custom errors for the Calculator
    '''

    pass

class ConfigurationError(CalculatorError):

    '''
    Raised when there is an invalid config setting
    '''

    pass

class OperationError(CalculatorError):

    '''
    Raised when a calculation operation fails
    '''

    pass

class ValidationError(CalculatorError):

    '''
    Raised when input validation fails
    '''

    pass

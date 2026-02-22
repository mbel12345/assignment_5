class CalculatorError(Exception):

    '''
    Base class for all other custom errors for the Calculator
    '''

    pass

class ValidationError(CalculatorError):

    '''
    Raised when input validation fails
    '''

    pass

import datetime

from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento

def test_memento_to_dict():

    # Test Memento to_dict

    memento = CalculatorMemento(
        history = [
            Calculation('Addition', 3, 5),
            Calculation('Subtraction', 2, 1),
        ],
    )

    actual = memento.to_dict()
    del(actual['timestamp'])
    for row in actual['history']:
        del(row['timestamp'])

    assert actual == {
        'history': [
            {
                'operation': 'Addition',
                'operand1': '3',
                'operand2': '5',
                'result': '8',
            },
            {
                'operation': 'Subtraction',
                'operand1': '2',
                'operand2': '1',
                'result': '1',
            }
        ]
    }

def test_memento_from_dict():

    # Test Memento from_dict

    data = {
        'history': [
            {
                'operation': 'Addition',
                'operand1': '3',
                'operand2': '5',
                'result': '8',
                'timestamp': datetime.datetime.now().isoformat(),
            },
            {
                'operation': 'Subtraction',
                'operand1': '2',
                'operand2': '1',
                'result': '1',
                'timestamp': datetime.datetime.now().isoformat(),
            }
        ],
        'timestamp': datetime.datetime.now().isoformat(),
    }

    actual = CalculatorMemento.from_dict(data)
    actual.history = [calc.to_dict() for calc in actual.history]
    assert actual.history == data['history']
    assert actual.timestamp.isoformat() == data['timestamp']

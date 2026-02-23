import datetime

from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.calculation import Calculation

@dataclass
class CalculatorMemento:

    '''
    Stores calculator states for undo/redo operations
    '''

    history: List[Calculation]
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_dict(self) -> Dict[str, Any]:

        # Convert Memento to dict

        return {
            'history': [calc.to_dict() for calc in self.history],
            'timestamp': self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalculatorMemento':

        # Create Memento from dict

        return cls(
            history=[Calculation.from_dict(calc) for calc in data['history']],
            timestamp=datetime.datetime.fromisoformat(data['timestamp'])
        )

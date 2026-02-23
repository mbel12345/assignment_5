import pandas as pd
import logging
import os

from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Union

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError
from app.exceptions import ValidationError
from app.history import HistoryObserver
from app.input_validators import InputValidator
from app.operations import Operation

Number = Union[int, float, Decimal]
CalculationResult = Union[Number, str]

class Calculator:

    '''
    Main calculator for the project, handling Operations, Observers, History, and most other features.
    '''

    def __init__(self, config: Optional[CalculatorConfig] = None):

        # Initialize Calculator

        if config is None:
            current_file = Path(__file__)
            project_root = current_file.parent.parent
            config = CalculatorConfig(base_dir=project_root)

        self.config = config
        self.config.validate()

        # Set up logging
        os.makedirs(self.config.log_dir, exist_ok=True)
        self._setup_logging()

        # Initialize calculation history and operation strategy
        self.history: List[Calculation] = []
        self.operation_strategy: Optional[Operation] = None

        # Initialize observers
        self.observers: List[HistoryObserver] = []

        # Initialize undo and redo stacks
        self.undo_stack: List[CalculatorMemento] = []
        self.redo_stack: List[CalculatorMemento] = []

        # Set up directories
        self._setup_directories()

        # Load history
        try:
            self.load_history()
        except Exception as e:
            logging.warning(f'Could not load existing history: {e}')

        logging.info('Calculator initialized with configuration')

    def _setup_logging(self) -> None:

        # Configure Calculator logging

        try:

            # Make sure log dir exists
            os.makedirs(self.config.log_dir, exist_ok=True)
            log_file = self.config.log_file.resolve()

            # Configure logging settings
            logging.basicConfig(
                filename=str(log_file),
                level = logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                force=True,
            )
            logging.info(f'Logging initialized at: {log_file}')

        except Exception as e:

            print(f'Error setting up logging: {e}')
            raise

    def _setup_directories(self) -> None:

        # Set up directory structure

        self.config.history_dir.mkdir(parents=True, exist_ok=True)

    def add_observer(self, observer: HistoryObserver) -> None:

        # Register a new observer

        self.observers.append(observer)
        logging.info(f'Added observer: {observer.__class__.__name__}')


    def remove_observer(self, observer: HistoryObserver) -> None:

        # Unregister a new observer

        self.observers.remove(observer)
        logging.info(f'Removed observer: {observer.__class__.__name__}')

    def notify_observers(self, calculation: Calculation) -> None:

        # Trigger an update to all observers whenever a new calc is done

        for observer in self.observers:
            observer.update(calculation)

    def set_operation(self, operation: Operation) -> None:

        # Set the operation strategy

        self.operation_strategy = operation
        logging.info(f'Set operation: {operation}')

    def perform_operation(
        self,
        a: Union[str, Number],
        b: Union[str, Number],
    ) -> CalculationResult:

        if not self.operation_strategy:
            raise OperationError('No operation set')

        try:

            validated_a = InputValidator.validate_number(a, self.config)
            validated_b = InputValidator.validate_number(b, self.config)

            result = self.operation_strategy.execute(validated_a, validated_b)

            calc = Calculation(
                operation=str(self.operation_strategy),
                operand1=validated_a,
                operand2=validated_b
            )

            # Save current state to undo_stack
            self.undo_stack.append(CalculatorMemento(self.history.copy()))

            # Clear the redo stash, since redos can only be done right after undos
            self.redo_stack.clear()

            # Add to history
            self.history.append(calc)
            if len(self.history) > self.config.max_history_size:
                self.history.pop(0)

            # Notify observers about the calc
            self.notify_observers(calc)

            return result

        except ValidationError as e:

            logging.error(f'Validation error: {str(e)}')
            raise

        except Exception as e:

            logging.error(f'Operation failed: {str(e)}')
            raise OperationError(f'Operation failed: {str(e)}')

    def save_history(self) -> None:

        # Save calculation history to csv

        try:

            self.config.history_dir.mkdir(parents=True, exist_ok=True)

            history_data = []
            for calc in self.history:
                history_data.append({
                    'operation': str(calc.operation),
                    'operand1': str(calc.operand1),
                    'operand2': str(calc.operand2),
                    'result': str(calc.result),
                    'timestamp': calc.timestamp.isoformat(),
                })

            if history_data:

                df = pd.DataFrame(history_data)
                df.to_csv(self.config.history_file, index=False)
                logging.info(f'History saved successfully to {self.config.history_file}')

            else:

                # Write csv with just the headers
                pd.DataFrame(columns=['operation', 'operand1', 'operand2', 'result', 'timestamp']).to_csv(self.config.history_file, index=False)
                logging.info('Empty history saved')

        except Exception as e:

            logging.error(f'Failed to save history: {e}')
            raise OperationError(f'Failed to save history: {e}')

    def load_history(self) -> None:

        # Read the history from the csv file if it exists

        try:

            if self.config.history_file.exists():

                df = pd.read_csv(self.config.history_file)
                if not df.empty:
                    self.history = [
                        Calculation.from_dict({
                            'operation': row['operation'],
                            'operand1': row['operand1'],
                            'operand2': row['operand2'],
                            'result': row['result'],
                            'timestamp': row['timestamp']
                        })
                        for _, row in df.iterrows()
                    ]
                    logging.info(f'Loaded {len(self.history)} calculations from history')
                else:
                    logging.info('Loaded empty history file')

            else:

                logging.info('No history file found - starting with empty history')

        except Exception as e:

            logging.error('Failed to load history: {e}')
            raise OperationError(f'Failed to load history: {e}')

    def get_history_dataframe(self) -> pd.DataFrame:

        # Load calculation history into a pandas DataFrame

        history_data = []
        for calc in self.history:
            history_data.append({
                'operation': str(calc.operation),
                'operand1': str(calc.operand1),
                'operand2': str(calc.operand2),
                'result': str(calc.result),
                'timestamp': calc.timestamp,
            })
        return pd.DataFrame(history_data)

    def show_history(self) -> List[str]:

        # Get formatted calculation history

        return [
            f'{calc.operation}({calc.operand1}, {calc.operand2}) = {calc.result}'
            for calc in self.history
        ]

    def clear_history(self) -> None:

        # Clear calculation history

        self.history.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        logging.info('History cleared')

    def undo(self) -> bool:

        # Undo the last operation

        if not self.undo_stack:
            return False

        memento = self.undo_stack.pop()
        self.redo_stack.append(CalculatorMemento(self.history.copy()))
        self.history = memento.history.copy()
        return True

    def redo(self) -> bool:

        # Redo the last undone operation

        if not self.redo_stack:
            return False

        memento = self.redo_stack.pop()
        self.undo_stack.append(CalculatorMemento(self.history.copy()))
        self.history = memento.history.copy()
        return True

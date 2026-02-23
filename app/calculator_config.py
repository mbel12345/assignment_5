import os

from dataclasses import dataclass
from decimal import Decimal
from dotenv import load_dotenv
from numbers import Number
from pathlib import Path
from typing import Optional

from app.exceptions import ConfigurationError

load_dotenv()

def get_project_root() -> Path:

    # Get the project root directory

    current_file = Path(__file__)

    return current_file.parent.parent

@dataclass
class CalculatorConfig:

    '''
    Set up config for the Calculator, from environment vars, .env files, etc.
    '''

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        max_history_size: Optional[int] = None,
        auto_save: Optional[bool] = None,
        precision: Optional[int] = None,
        max_input_value: Optional[Number] = None,
        default_encoding: Optional[str] = None,
    ):

        # Load vars from either __init__ parameters of environment vars

        project_root = get_project_root()
        self.base_dir = base_dir or Path(os.getenv('CALCULATOR_BASE_DIR', str(project_root))).resolve()
        self.max_history_size = max_history_size or int(os.getenv('CALCULATOR_MAX_HISTORY_SIZE', '1000'))
        self.auto_save = auto_save if auto_save is not None else os.getenv('CALCULATOR_AUTO_SAVE', 'true').lower() in ['true', '1']
        self.precision = precision or int(os.getenv('CALCULATOR_PRECISION', '10'))
        self.max_input_value = max_input_value or Decimal(os.getenv('CALCULATOR_MAX_INPUT_VALUE', '1e999'))
        self.default_encoding = default_encoding or os.getenv('CALCULATOR_DEFAULT_ENCODING', 'utf-8')

    @property
    def log_dir(self) -> Path:

        # Return a Path where logs will be stored

        return Path(os.getenv('CALCULATOR_LOG_DIR', str(self.base_dir / 'logs'))).resolve()

    @property
    def log_file(self) -> Path:

        # Return a file path where logs will be stored
        return Path(os.getenv('CALCULATOR_LOG_FILE', str(self.log_dir / 'calculator.log'))).resolve()

    @property
    def history_dir(self) -> Path:

        # Return a Path where history will be stored

        return Path(os.getenv('CALCULATOR_HISTORY_DIR', str(self.base_dir / 'history'))).resolve()

    @property
    def history_file(self) -> Path:

        # Return a file path where history will be stored

        return Path(os.getenv('CALCULATOR_HISTORY_FILE', str(self.history_dir / 'calculator_history.csv'))).resolve()

    def validate(self) -> None:

        # Validate the settings

        if self.max_history_size <= 0:
            raise ConfigurationError('max_history_size must be positive')

        if self.precision <= 0:
            raise ConfigurationError('precision must be positive')

        if self.max_input_value <= 0:
            raise ConfigurationError('max_input_value must be positive')

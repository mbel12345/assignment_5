from decimal import Decimal
import logging

from app.calculator import Calculator
from app.exceptions import OperationError
from app.exceptions import ValidationError
from app.history import AutoSaveObserver
from app.history import LoggingObserver
from app.operations import OperationFactory

'''
REPL calculator that can perform Add, Subtract, Multiply, Divide, Power, Root. Stores history and logs all operations.
'''

def calculator_repl():

    try:

        calc = Calculator()

        # Register observers
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        print('Calculator started. Type \'help\' for commands')

        while True:

            try:

                command = input('\nEnter command: ').lower().strip()

                if command == 'help':
                    # Display allowed commands
                    print("\nAvailable commands:")
                    print("  add, subtract, multiply, divide, power, root - Perform calculations")
                    print("  history - Show calculation history")
                    print("  clear - Clear calculation history")
                    print("  undo - Undo the last calculation")
                    print("  redo - Redo the last undone calculation")
                    print("  save - Save calculation history to file")
                    print("  load - Load calculation history from file")
                    print("  exit - Exit the calculator")
                    continue

                if command == 'exit':
                    try:
                        calc.save_history()
                        print('History saved successfully')
                    except Exception as e:
                        print(f'Warning: Could not save history: {e}')
                    print('Goodbye!')
                    break

                if command == 'history':
                    history = calc.show_history()
                    if not history:
                        print('No calculations in history')
                    else:
                        print('\nCalculation History:')
                        for i, entry in enumerate(history, i):
                            print(f'{i}. {entry}')
                    continue

                if command == 'clear':
                    calc.clear_history()
                    print('History cleared')
                    continue

                if command == 'undo':
                    if calc.undo():
                        print('Operation undone')
                    else:
                        print('Nothing to undo')
                    continue

                if command == 'redo':
                    if calc.redo():
                        print('Operation redone')
                    else:
                        print('Nothing to redo')
                    continue

                if command == 'save':
                    try:
                        calc.save_history()
                        print('History saved successfully')
                    except Exception as e:
                        print(f'Error saving history: {e}')
                    continue

                if command == 'load':
                    try:
                        calc.load_history()
                        print('History loaded successfully')
                    except Exception as e:
                        print(f'Error loading history: {e}')
                    continue

                if command in ['add', 'subtract', 'multiply', 'divide', 'power', 'root']:
                    try:
                        print("\nEnter numbers (or 'cancel'; to abort):")
                        a = input('First number: ')
                        if a.lower() == 'cancel':
                            print('Operation cancelled')
                            continue
                        b = input('Second number: ')
                        if b.lower() == 'cancel':
                            print('Operation cancelled')
                            continue

                        # Create the appropriate operation using a Factory
                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)

                        # Perform the calculation
                        result = calc.perform_operation(a, b)

                        # Normalize
                        if isinstance(result, Decimal):
                            result = result.normalize()

                        print(f'\nResult: {result}')

                    except (ValidationError, OperationError) as e:
                        print(f'Error: {e}')

                    except Exception as e:
                        print(f'Unexpected error: {e}')

                    continue

                print(f"Unknown command: '{command}'. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print('\nOperation cancelled')

            except EOFError:
                print('\nInput terminated. Exiting...')

            except Exception as e:
                print(f'Error: {e}')
                continue

    except Exception as e:

        # Fatal errors

        print(f'Fatal error: {e}')
        logging.error(f'Fatal error in calculator REPL: {e}')

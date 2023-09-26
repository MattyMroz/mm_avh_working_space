"""
    Module execution_timer provides an ExecutionTimer class
        to measure the execution time of a code block.
    It offers two usage options: as a context manager and as a decorator.

    * Example usage as a context manager:
        with ExecutionTimer():
            main()

    * Example usage as a decorator:
        @execution_timer
        def main():
            # Code block to measure execution time
"""

from datetime import datetime
from time import perf_counter_ns

from dataclasses import dataclass
from rich.console import Console


@dataclass(slots=True)
class ExecutionTimer:
    """
        ExecutionTimer is a context manager that measures the execution time of a code block.
        It captures the start time, end time, and duration of the code block.
    """

    start_date: datetime = None
    end_date: datetime = None
    start_time_ns: int = None
    end_time_ns: int = None
    console: Console = Console()

    def __post_init__(self):
        self.start_date = datetime.now()
        self.start_time_ns = perf_counter_ns()

    def __enter__(self) -> 'ExecutionTimer':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.end_date = datetime.now()
            self.end_time_ns = perf_counter_ns()
            self.display_time()
        except AttributeError:
            print('An error occurred: __exit__')

    @staticmethod
    def current_datetime(date: datetime) -> str:
        """
            Formats a datetime object as a string in the format 'YYYY-MM-DD HH:MM:SS'.
        """

        return f'[yellow]{date.year}-{date.month:02d}-{date.day:02d}' \
               f' [white bold]{date.hour:02d}:{date.minute:02d}:{date.second:02d}'

    def calculate_duration(self) -> str:
        """
            Calculates the duration of the code block in hours, minutes, seconds, milliseconds,
            microseconds, and nanoseconds.
        """

        duration_ns: int = self.end_time_ns - self.start_time_ns
        duration_s, duration_ns = map(int, divmod(duration_ns, 1_000_000_000))
        duration_ms, duration_ns = map(int, divmod(duration_ns, 1_000_000))
        duration_us, duration_ns = map(int, divmod(duration_ns, 1_000))

        hours, remainder = map(int, divmod(duration_s, 3600))
        minutes, seconds = map(int, divmod(remainder, 60))

        return f'[white bold]{hours:02d}:{minutes:02d}:{seconds:02d}:' \
               f'{duration_ms:03d}:{duration_us:03d}:{duration_ns:03d}'

    def calculate_duration_alt(self) -> tuple[float, ...]:
        """
            Calculates the duration of the code block in hours, minutes, and seconds
            using an alternative method.
        """

        duration_ns: int = self.end_time_ns - self.start_time_ns
        hours_alt: float = duration_ns / 1_000_000_000 / 60 / 60
        minutes_alt: float = duration_ns / 1_000_000_000 / 60
        seconds_alt: float = duration_ns / 1_000_000_000

        return hours_alt, minutes_alt, seconds_alt

    def display_time(self):
        """
            Displays the start date, end date, and duration of the code block execution.
        """

        start_date_str: str = self.current_datetime(self.start_date)
        end_date_str: str = self.current_datetime(self.end_date)
        duration: str = self.calculate_duration()
        hours_alt, minutes_alt, seconds_alt = map(
            float, self.calculate_duration_alt())

        self.console.print(
            '\n[bold white]╚═══════════ EXECUTION TIME ═══════════╝')
        self.console.print(
            '[bold bright_yellow]        YYYY-MM-DD HH:MM:SS:ms :µs :ns')
        self.console.print(
            f'[bright_red bold][[bold white]START[bright_red bold]] {start_date_str}')
        self.console.print(
            f'[bright_red bold][[bold white]END[bright_red bold]]   {end_date_str}')
        self.console.print(
            f'[bright_red bold][[bold white]TIME[bright_red bold]]  [bold bright_yellow]YYYY-MM-DD {duration}')
        self.console.print('[bright_red bold]                   ^^^^^^^^^^^^')
        self.console.print(
            f'[bright_red bold][[bold white]TIME[bright_red bold]]  [white bold]{hours_alt:.9f} hours')
        self.console.print(
            f'[bright_red bold][[bold white]TIME[bright_red bold]]  [white bold]{minutes_alt:.9f} minutes')
        self.console.print(
            f'[bright_red bold][[bold white]TIME[bright_red bold]]  [white bold]{seconds_alt:.9f} seconds')


def execution_timer(func):
    """
        Decorator that measures the execution time of a function using ExecutionTimer.
    """

    def wrapper(*args, **kwargs):
        with ExecutionTimer():
            result = func(*args, **kwargs)
        return result

    return wrapper

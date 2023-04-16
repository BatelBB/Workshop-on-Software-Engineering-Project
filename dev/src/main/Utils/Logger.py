import queue
import threading
from datetime import datetime
from enum import Enum
from typing import TypeVar

from dev.src.main.Utils.IConcurrentSingelton import IConcurrentSingleton
from dev.src.main.Utils.Response import Response


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


def getdate():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


class Logger(metaclass=IConcurrentSingleton):
    class Severity(Enum):
        INFO = '\033[97m'  # WHITE
        WARNING = '\033[93m'  # YELLOW
        ERROR = '\033[91m'  # Red
        DEBUG = '\033[97m'  # CYAN
        SUCCEED = '\033[92m'  # GREEN
        ENDLINE = '\033[0m'

    def __init__(self, filename: str = "WorkshopLog.txt", print_to_stdout: bool = True):
        self.queue = queue.Queue()
        self.logfile = open(filename, "wt")
        self.print_to_stdout = print_to_stdout
        self.run = True
        self.condition_variable = threading.Condition()
        self.thread_handler = self.log()

    def notify(self):
        with self.condition_variable:
            self.condition_variable.notify()

    def post(self, msg: str, severity: Severity = Severity.INFO):
        self.queue.put((msg, severity))
        self.notify()

    def shutdown(self):
        self.run = False
        self.notify()
        self.thread_handler.join()
        self.logfile.close()

    def get_severity_name(self, severity: Severity) -> str:
        return self.Severity(severity).name

    def get_severity_color(self, severity: Severity) -> str:
        return self.Severity(severity).value

    def create_message(self, msg: str, severity: Severity = Severity.INFO) -> str:
        return f'{getdate()} {self.get_severity_name(severity)}:\t {msg}'

    def create_colored_message(self, msg: str, severity: Severity = Severity.INFO) -> str:
        return f'{self.get_severity_color(severity)}{msg}{self.get_severity_color(severity.ENDLINE)}'

    def write(self):
        msg, severity = self.queue.get()
        msg = self.create_message(msg, severity)
        self.logfile.write(f'{msg}\n')
        if self.print_to_stdout:
            print(self.create_colored_message(msg, severity))

    def dismiss(self):
        self.queue.put(('Logger thread exits!', self.Severity.WARNING))
        while not self.queue.empty():
            self.write()

    @threaded
    def log(self) -> None:
        while self.run:
            while self.queue.empty() and self.run:
                with self.condition_variable:
                    self.condition_variable.wait()
            if self.run:  # we might shut down a thread while its queue is empty
                self.write()
            else:
                break
        self.dismiss()


Result = TypeVar("Result")


def report(msg: str, result: Result, severity: Logger.Severity = Logger.Severity.INFO) -> Response[Result]:
    Logger().post(msg, severity)
    return Response(result, msg)


def report_error(calling_method_name: str, error_description: str) -> Response[bool]:
    return report(f'{calling_method_name}: {error_description}', False, Logger.Severity.ERROR)


def report_warning(calling_method_name: str, error_description: str) -> Response[bool]:
    return report(f'{calling_method_name}: {error_description}', False, Logger.Severity.WARNING)


def report_info(calling_method_name: str, error_description: str) -> Response[bool]:
    return report(f'{calling_method_name}: {error_description}', True, Logger.Severity.INFO)


def report_debug(calling_method_name: str, error_description: str) -> Response[bool]:
    return report(f'{calling_method_name}: {error_description}', False, Logger.Severity.DEBUG)

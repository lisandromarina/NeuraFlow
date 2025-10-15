# core/logger.py
import datetime
import threading

class Logger:
    def __init__(self, prefix="[Workflow]", thread_safe=True):
        self.prefix = prefix
        self.thread_safe = thread_safe

    def log(self, msg: str, indent_level=0):
        indent = "  " * indent_level
        thread_name = threading.current_thread().name
        timestamp = datetime.datetime.now().isoformat()
        print(f"{timestamp} {self.prefix} [{thread_name}] {indent}{msg}", flush=True)

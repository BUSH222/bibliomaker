class Logger:
    """The class for logging informational messages, used for debugging."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def __init__(self, verbosity: bool, pure=True) -> None:
        self.verbosity = verbosity
        self.pure = pure

    def log(self, text, color=HEADER):
        if self.verbosity and not self.pure:
            print(f"{color} {text} {self.ENDC}")
        elif self.verbosity and self.pure:
            print(f"LOG: {text}")

    def fail(self, text, color=FAIL):
        if self.verbosity and not self.pure:
            print(f"{color} {text} {self.ENDC}")
        elif self.verbosity and self.pure:
            print(f"FAIL: {text}")

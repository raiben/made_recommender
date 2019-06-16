from contextlib import contextmanager

@contextmanager
def write_stdout_through_logger(logger):
    import sys
    old_stdout = sys.stdout
    class CustomPrint():
        def __init__(self, stdout):
            self.old_stdout = stdout

        def write(self, text):
            if len(text.rstrip()):
                logger.info(text)

    sys.stdout = CustomPrint(old_stdout)

    try:
        yield
    finally:
        sys.stdout = old_stdout

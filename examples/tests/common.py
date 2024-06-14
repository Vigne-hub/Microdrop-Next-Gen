import os
from contextlib import contextmanager
from dramatiq import Worker


@contextmanager
def worker(*args, **kwargs):
    try:
        worker = Worker(*args, **kwargs)
        worker.start()
        yield worker
    finally:
        worker.stop()

TEST_PATH = os.getenv("TEST_PATH", os.path.dirname(os.path.abspath(__file__)))

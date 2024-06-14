import pytest
import dramatiq
from dramatiq import Worker
from dramatiq.brokers.stub import StubBroker
from dramatiq.rate_limits import backends as rl_backends
from dramatiq.results import backends as res_backends

@pytest.fixture()
def stub_broker():
    broker = StubBroker()
    broker.emit_after("process_boot")
    dramatiq.set_broker(broker)
    yield broker
    broker.flush_all()
    broker.close()


@pytest.fixture()
def stub_worker(stub_broker):
    worker = Worker(stub_broker, worker_timeout=100, worker_threads=32)
    worker.start()
    yield worker
    worker.stop()


@pytest.fixture
def stub_rate_limiter_backend():
    return rl_backends.StubBackend()


@pytest.fixture
def stub_result_backend():
    return res_backends.StubBackend()


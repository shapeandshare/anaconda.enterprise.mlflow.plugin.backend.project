import os
import warnings

from ae5_tools.api import AEUserSession

from src.anaconda.enterprise.mlflow.plugin.backend.project.utils import create_session

warnings.filterwarnings("ignore", category=DeprecationWarning)


class MockState(object):
    calls = []
    responses = []

    @classmethod
    def mockreturn(cls, *args, **kwargs):
        cls.calls.append([args, kwargs])
        return cls.responses.pop()

    @classmethod
    def reset(cls):
        cls.calls = []
        cls.responses = []


def test_create_session(monkeypatch):
    # Setup Test
    MockState.reset()
    MockState.responses = [None]
    monkeypatch.setattr(AEUserSession, "_connect", MockState.mockreturn)

    # Execute Test
    session: AEUserSession = create_session()

    # Review Test Outcome
    assert len(MockState.calls) == 1

    generated_session: AEUserSession = MockState.calls[0][1]["password"]
    assert session.hostname == generated_session.hostname == os.environ["AE5_HOSTNAME"]
    assert session.username == generated_session.username == os.environ["AE5_USERNAME"]
    assert session.password == generated_session.password == os.environ["AE5_PASSWORD"]

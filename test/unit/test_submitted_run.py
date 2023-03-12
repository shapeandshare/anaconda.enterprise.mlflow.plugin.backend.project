import uuid
from typing import Dict, List
from unittest.mock import MagicMock

import pytest
from ae5_tools.api import AEUserSession

from mlflow_adsp.contacts.errors.plugin import AEMLFlowPluginError
from mlflow_adsp.submitted_run import AnacondaEnterpriseSubmittedRun


@pytest.fixture(scope="function")
def get_token_fixture():
    return {
        "access_token": str(uuid.uuid4()),
        "refresh_token": str(uuid.uuid4()),
    }


@pytest.fixture(scope="function")
def get_ae_user_session(get_token_fixture) -> AEUserSession:
    user_session = AEUserSession(
        hostname="MOCK-HOSTNAME", username="MOCK-AE-USERNAME", password="MOCK-AE-USER-PASSWORD"
    )
    user_session._load = MagicMock()
    user_session._sdata = get_token_fixture
    return user_session


@pytest.fixture(scope="function")
def submitted_run(get_ae_user_session) -> AnacondaEnterpriseSubmittedRun:
    mock_mlflow_run_id: str = str(uuid.uuid4())
    mock_ae_job_id: str = str(uuid.uuid4())
    mock_response: Dict = {}

    submitted_run: AnacondaEnterpriseSubmittedRun = AnacondaEnterpriseSubmittedRun(
        ae_session=get_ae_user_session,
        mlflow_run_id=mock_mlflow_run_id,
        ae_job_id=mock_ae_job_id,
        response=mock_response,
    )

    return submitted_run


def test_get_log_missing_run(submitted_run):
    """ """
    # Set up the scenario
    submitted_run.ae_session.job_runs = MagicMock(return_value=[])

    # Execute the test
    with pytest.raises(AEMLFlowPluginError):
        submitted_run.get_log()


def test_get_log(submitted_run):
    """ """
    # Set up the scenario
    mock_job_runs: List[Dict] = [{"id": str(uuid.uuid4())}]
    mock_job_log: str = "mock logs"
    submitted_run.ae_session.job_runs = MagicMock(return_value=mock_job_runs)
    submitted_run.ae_session.run_log = MagicMock(return_value=mock_job_log)

    # Execute the test
    generated_log: str = submitted_run.get_log()

    # Review the results
    assert generated_log == mock_job_log
    submitted_run.ae_session.job_runs.assert_called_once_with(ident=submitted_run.ae_job_id, format="json")
    submitted_run.ae_session.run_log.assert_called_once_with(ident=mock_job_runs[0]["id"])

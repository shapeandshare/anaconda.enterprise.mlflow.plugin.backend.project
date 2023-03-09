""" Anaconda Enterprise Submitted Run Definition """

import logging
import time
from typing import Dict, List

from ae5_tools.api import AEUserSession
from mlflow.entities import RunStatus
from mlflow.projects.submitted_run import SubmittedRun

from anaconda.enterprise.server.contracts import BaseModel

logger = logging.getLogger(__name__)


class AnacondaEnterpriseSubmittedRun(SubmittedRun, BaseModel):
    """
    Anaconda Enterprise Submitted Run
    Sub-classes the MLFlow `SubmittedRun` used for backend management.

    Attributes
    ----------
    ae_session: AEUserSession
        An Anaconda Enterprise session used for communication with the platform.
    mlflow_run_id: str
        The MLFlow Run ID for the current context.
    ae_job_id: str
        The Anaconda Enterprise Job ID
    response: Dict
        A dictionary response of the job creation request.
    """

    ae_session: AEUserSession
    mlflow_run_id: str
    ae_job_id: str
    response: Dict

    def get_log(self) -> str:
        """
        Gets the [current] logs for the job run.

        Returns
        -------
        log: str
            A string representation of the run output.
        """

        runs_status: List[Dict] = self.ae_session.job_runs(ident=self.ae_job_id, format="json")
        if len(runs_status) != 1:
            raise Exception("Unable to determine which run to analyze")
        run_id: str = runs_status[0]["id"]
        return self.ae_session.run_log(ident=run_id)

    def wait(self) -> bool:
        """
        Waits for the run to complete then returns the success status.

        Returns
        -------
        success: bool
            Returns True/False based on successful run execution.
        """

        self._wait_on_job_run()

        runs_status: List[Dict] = self.ae_session.job_runs(ident=self.ae_job_id, format="json")
        if len(runs_status) != 1:
            raise Exception("Unable to determine which run to analyze")

        job_status: str = runs_status[0]["state"]
        if job_status == "completed":
            return True
        return False

    def _wait_on_job_run(self) -> None:
        """Blocks while the run is still in active execution."""

        completed: bool = False
        wait_interval: int = 60  # 60 seconds

        while not completed:
            time.sleep(wait_interval)

            runs_status: List[Dict] = self.ae_session.job_runs(ident=self.ae_job_id, format="json")
            if len(runs_status) != 1:
                raise Exception("Unable to determine which job to analyze")

            job_status: str = runs_status[0]["state"]
            if job_status in ["failed", "stopped", "completed"]:
                completed = True

    def get_status(self) -> RunStatus:
        """
        Gets the current status of the run.

        Returns
        -------
        status: RunStatus
            Returns an MLFlow run status for the Anaconda Enterprise run status.
        """

        runs_status: List[Dict] = self.ae_session.job_runs(ident=self.ae_job_id, format="json")

        if len(runs_status) != 1:
            raise Exception("Unable to determine which run to analyze")

        job_status: str = runs_status[0]["state"]

        if job_status == "running":
            return RunStatus.RUNNING

        if job_status == "failed":
            return RunStatus.FAILED

        if job_status == "stopped":
            return RunStatus.KILLED

        if job_status == "completed":
            return RunStatus.FINISHED

        message: str = f"Unknown job state seen: ({job_status})"
        raise Exception(message)

    def cancel(self) -> None:
        """Cancels a run's execution"""

        self.ae_session.run_stop(ident=self.ae_job_id)

    @property
    def run_id(self):
        """
        `run_id` Property

        Returns
        -------
        run_id: str
            The MLFlow Run ID for the context.
        """

        return self.mlflow_run_id

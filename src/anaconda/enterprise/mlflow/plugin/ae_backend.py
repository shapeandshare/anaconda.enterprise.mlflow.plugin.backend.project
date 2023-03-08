import json
import logging
import os
import time
from typing import Dict, List

from ae5_tools.api import AEUserSession
from mlflow.entities import RunStatus
from mlflow.projects.backend.abstract_backend import AbstractBackend
from mlflow.projects.submitted_run import SubmittedRun
from mlflow.projects.utils import PROJECT_STORAGE_DIR, fetch_and_validate_project, get_or_create_run, load_project

from anaconda.enterprise.server.common.sdk import demand_env_var
from anaconda.enterprise.server.contracts import BaseModel

logger = logging.getLogger(__name__)


def session_factory():
    # Create the session directly and provide the AE5 config and credentials:
    ae_session: AEUserSession = AEUserSession(
        hostname=os.environ["AE5_HOSTNAME"], username=os.environ["AE5_USERNAME"], password=os.environ["AE5_PASSWORD"]
    )

    # Connect to Anaconda Enterprise
    ae_session._connect(password=ae_session)
    return ae_session


def ae_backend_builder() -> AbstractBackend:
    return AnacondaEnterpriseProjectBackend(ae_session=session_factory())


class AnacondaEnterpriseSubmittedRun(SubmittedRun, BaseModel):
    """
    A run that just does nothing
    """

    ae_session: AEUserSession
    mlflow_run_id: str
    ae_job_id: str
    response: Dict

    def log(self):
        return self.ae_session.run_log(ident=self.ae_job_id)

    def wait(self) -> bool:
        self._wait_on_job_run()

        runs_status: List[Dict] = self.ae_session.job_runs(ident=self.ae_job_id, format="json")

        if len(runs_status) > 1:
            raise Exception("Unable to determine which run to analyze")

        job_status: str = runs_status[0]["state"]

        if job_status == "completed":
            return True

        return False

    def _wait_on_job_run(self) -> None:
        completed: bool = False
        wait_interval: int = 5

        while not completed:
            time.sleep(wait_interval)
            runs_status: List[Dict] = self.ae_session.job_runs(ident=self.ae_job_id, format="json")
            if len(runs_status) > 1:
                raise Exception("Unable to determine which run to analyze")
            job_status: str = runs_status[0]["state"]

            if job_status in ["failed", "stopped", "completed"]:
                completed = True

    def get_status(self) -> RunStatus:
        runs_status: List[Dict] = self.ae_session.job_runs(ident=self.ae_job_id, format="json")

        if len(runs_status) > 1:
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
        self.ae_session.run_stop(ident=self.ae_job_id)

    @property
    def run_id(self):
        return self.mlflow_run_id


class AnacondaEnterpriseProjectBackend(AbstractBackend, BaseModel):
    ae_session: AEUserSession

    def run(
        self,
        project_uri: str,
        entry_point: str,
        params: Dict,
        version: str,
        backend_config: Dict,
        tracking_uri: str,
        experiment_id: str,
    ):
        logger.info("Using Anaconda Enterprise Backend")
        # logger.info(locals())

        work_dir = fetch_and_validate_project(project_uri, version, entry_point, params)
        active_run = get_or_create_run(None, project_uri, experiment_id, work_dir, version, entry_point, params)

        logger.info(f"run_id={active_run.info.run_id}")
        logger.info(f"work_dir={work_dir}")
        project = load_project(work_dir)

        storage_dir = backend_config[PROJECT_STORAGE_DIR]
        entry_point_command = project.get_entry_point(entry_point).compute_command(params, storage_dir)
        logger.info(f"entry_point_command={entry_point_command}")

        env_vars: Dict = {
            "MLFLOW_RUN_ID": active_run.info.run_id,
            "MLFLOW_EXPERIMENT_ID": experiment_id,
        }

        job_create_response = self.submit_job(
            mlflow_run_id=active_run.info.run_id, variables={**env_vars, "TRAINING_ENTRY_POINT": entry_point_command}
        )

        return AnacondaEnterpriseSubmittedRun(
            ae_session=self.ae_session,
            mlflow_run_id=active_run.info.run_id,
            ae_job_id=job_create_response["id"],
            response=job_create_response,
        )

    def submit_job(self, mlflow_run_id: str, variables: Dict) -> Dict:
        # Create a run-now job
        job_create_result: Dict = self.ae_session.job_create(
            ident=AnacondaEnterpriseProjectBackend.get_project_id(),
            name=mlflow_run_id,
            command="Worker",
            variables=variables,
            run=True,
            format=format,
        )
        return job_create_result

    @staticmethod
    def get_project_id() -> str:
        return f"a0-{demand_env_var(name='TOOL_PROJECT_URL').split(sep='/')[4]}"

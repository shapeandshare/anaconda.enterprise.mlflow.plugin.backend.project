import json
import logging
import os
from typing import Dict, Optional

import mlflow
from mlflow.entities import RunStatus
from mlflow.projects.backend.abstract_backend import AbstractBackend
from mlflow.projects.submitted_run import SubmittedRun
from mlflow.projects.utils import PROJECT_STORAGE_DIR, fetch_and_validate_project, get_or_create_run, load_project

from anaconda.enterprise.server.contracts import BaseModel
from anaconda.enterprise.server.sdk import AEClient

from .utils import get_ae_client

logger = logging.getLogger(__name__)

ae_client: Optional[AEClient] = None


def ae_backend_builder() -> AbstractBackend:
    global ae_client
    if not ae_client:
        ae_client = get_ae_client()
    return AnacondaEnterpriseProjectBackend(ae_client=ae_client)


class AnacondaEnterpriseSubmittedRun(SubmittedRun, BaseModel):
    """
    A run that just does nothing
    """

    mlflow_run_id: str

    def wait(self) -> bool:
        # TODO: Should allow blocking until the AE job has completed
        return True

    def get_status(self) -> RunStatus:
        # TODO: Should translate from AE job status to MLFlow status
        return RunStatus.FINISHED

    def cancel(self) -> None:
        # TODO: Should allow forcibly terminating the job.
        pass

    @property
    def run_id(self):
        return self.mlflow_run_id


class AnacondaEnterpriseProjectBackend(AbstractBackend, BaseModel):
    ae_client: AEClient

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
        logger.info(locals())

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
            "MLFLOW_TRACKING_URI": mlflow.get_tracking_uri(),
            "MLFLOW_EXPERIMENT_ID": experiment_id,
        }

        _backend_dict: Dict = _get_backend_dict(work_dir)
        # update config with what has been passed with --backend-config <json-new-config>
        for key in _backend_dict:
            if key in backend_config:
                _backend_dict[key] = backend_config[key]
        logger.info(f"backend config: {_backend_dict}")

        # TODO: SUBMIT AE JOB

        return AnacondaEnterpriseSubmittedRun(mlflow_run_id=active_run.info.run_id)


#  https://github.com/criteo/mlflow-yarn/blob/master/mlflow_yarn/yarn_backend.py#L170
def _get_backend_dict(work_dir: str) -> Dict:
    backend_config = os.path.join(work_dir, "backend_config.json")
    if os.path.exists(backend_config):
        try:
            with open(backend_config, "r") as f:
                backend_config_dict: Dict = json.load(f)
                if not isinstance(backend_config_dict, dict):
                    raise ValueError(f"{backend_config} file must be a dict")
                return backend_config_dict
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse {backend_config}", exc_info=e)
            return {}
    return {}

import logging
from typing import Dict, Optional, Union

from ae5_tools.api import AEUserSession
from mlflow.entities import Run
from mlflow.projects._project_spec import Project
from mlflow.projects.backend.abstract_backend import AbstractBackend
from mlflow.projects.utils import PROJECT_STORAGE_DIR, fetch_and_validate_project, get_or_create_run, load_project

from anaconda.enterprise.server.common.sdk import demand_env_var
from anaconda.enterprise.server.contracts import BaseModel

from .ae_submitted_run import AnacondaEnterpriseSubmittedRun
from .utils import create_session

logger = logging.getLogger(__name__)


def ae_backend_builder() -> AbstractBackend:
    return AnacondaEnterpriseProjectBackend(ae_session=create_session())


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

        work_dir: Union[bytes, str] = fetch_and_validate_project(project_uri, version, entry_point, params)
        active_run: Run = get_or_create_run(
            run_id=None,
            uri=project_uri,
            experiment_id=experiment_id,
            work_dir=work_dir,
            version=version,
            entry_point=entry_point,
            parameters=params,
        )

        logger.info(f"run_id={active_run.info.run_id}")
        logger.info(f"work_dir={work_dir}")

        project: Project = load_project(work_dir)

        storage_dir: Dict = backend_config[PROJECT_STORAGE_DIR]
        entry_point_command: str = project.get_entry_point(entry_point).compute_command(params, storage_dir)
        logger.info(f"entry_point_command={entry_point_command}")

        # MLFlow Session Variables Needed For Reporting
        env_vars: Dict = {
            "MLFLOW_RUN_ID": active_run.info.run_id,
            "MLFLOW_EXPERIMENT_ID": experiment_id,
        }

        # Resource profiles can be defined within backend_config.json
        resource_profile: Optional[str] = (
            backend_config["resource_profile"] if "resource_profile" in backend_config else None
        )

        # Submit the job to Anaconda Enterprise
        job_create_response: Dict = self.submit_job(
            mlflow_run_id=active_run.info.run_id,
            variables={**env_vars, "TRAINING_ENTRY_POINT": entry_point_command},
            resource_profile=resource_profile,
        )

        return AnacondaEnterpriseSubmittedRun(
            ae_session=self.ae_session,
            mlflow_run_id=active_run.info.run_id,
            ae_job_id=job_create_response["id"],
            response=job_create_response,
        )

    def submit_job(
        self, mlflow_run_id: str, resource_profile: Optional[str] = None, variables: Optional[Dict] = None
    ) -> Dict:
        # Create a run-now job
        job_create_result: Dict = self.ae_session.job_create(
            ident=AnacondaEnterpriseProjectBackend.get_project_id(),
            name=mlflow_run_id,
            command="Worker",
            resource_profile=resource_profile,
            variables=variables,
            run=True,
            format=format,
        )
        return job_create_result

    @staticmethod
    def get_project_id() -> str:
        # When executing within a session this seems to be the most reliable method for getting a context id.
        return f"a0-{demand_env_var(name='TOOL_PROJECT_URL').split(sep='/')[4]}"

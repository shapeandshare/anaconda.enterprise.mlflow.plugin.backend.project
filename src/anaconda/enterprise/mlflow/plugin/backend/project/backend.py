""" MLFlow Backend Plugin For Anaconda Enterprise Definition """

import logging
from typing import Dict, Optional, Union

from ae5_tools.api import AEUserSession
from mlflow.entities import Run
from mlflow.projects._project_spec import Project
from mlflow.projects.backend.abstract_backend import AbstractBackend
from mlflow.projects.utils import PROJECT_STORAGE_DIR, fetch_and_validate_project, get_or_create_run, load_project

from anaconda.enterprise.server.common.sdk import demand_env_var
from anaconda.enterprise.server.contracts import BaseModel

from .submitted_run import AnacondaEnterpriseSubmittedRun
from .utils import create_session

logger = logging.getLogger(__name__)


def ae_backend_builder() -> AbstractBackend:
    """
    This function will act as our handler for setting up the plugin.

    This function is responsible for:
    1. Creating an Anaconda Enterprise Session and Connecting.
    2. Instantiating an AnacondaEnterpriseProjectBackend with the created session.

    Returns
    -------
    backend: AnacondaEnterpriseProjectBackend
        An instance of the plugin.
    """

    return AnacondaEnterpriseProjectBackend(ae_session=create_session())


class AnacondaEnterpriseProjectBackend(AbstractBackend, BaseModel):
    """
    Anaconda Enterprise Project Backend
    Sub-classes the MLFlow `AbstractBackend` used for backend management.
    """

    ae_session: AEUserSession

    # Note: this function's signature is defined by the super-class and is expected
    # to be able to receive these arguments, we can not adjust this here.
    # pylint: disable=too-many-arguments
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
        """
        The entry point for the execution.  Invoked by mlflow.projects.run when the backend is specified.
        See https://mlflow.org/docs/2.0.1/python_api/mlflow.projects.html#mlflow.projects.run for
        in-depth details on these parameters.

        Parameters
        ----------
        project_uri: str
            URI of project to run.
        entry_point: str
            Entry point to run within the project.
        params: Dict
            Parameters (dictionary) for the entry point command.
        version: str
            For Git-based projects, either a commit hash or a branch name.
        backend_config: Dict
            A dictionary, or a path to a JSON file (must end in ‘.json’), which will be passed as config to the backend.
        tracking_uri: str
            The Tracking Server URI.  Within our backend this is controlled through environment variables.
            While passed by the caller it is ignored in this implementation.
        experiment_id: str
            The experiment ID for the current execution context.

        Returns
        -------
        submitted_job: AnacondaEnterpriseSubmittedRun
            An instance of an `AnacondaEnterpriseSubmittedRun` used for tracking and managing the backend run.
        """

        logger.debug("Using Anaconda Enterprise Backend")

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

        logger.debug(active_run.info.run_id)
        logger.debug(work_dir)

        # MLFlow Session Variables
        entry_point_cmd: str = self._get_entry_point_command(
            work_dir=work_dir, backend_config=backend_config, entry_point=entry_point, params=params
        )
        env_vars: Dict = {
            "MLFLOW_RUN_ID": active_run.info.run_id,
            "MLFLOW_EXPERIMENT_ID": experiment_id,
            "TRAINING_ENTRY_POINT": entry_point_cmd,
        }

        # Resource profiles can be defined within backend_config.json
        resource_profile: Optional[str] = (
            backend_config["resource_profile"] if "resource_profile" in backend_config else None
        )

        # Submit the job to Anaconda Enterprise
        job_create_response: Dict = self._submit_job(
            mlflow_run_id=active_run.info.run_id,
            variables=env_vars,
            resource_profile=resource_profile,
        )

        return AnacondaEnterpriseSubmittedRun(
            ae_session=self.ae_session,
            mlflow_run_id=active_run.info.run_id,
            ae_job_id=job_create_response["id"],
            response=job_create_response,
        )

    @staticmethod
    def _get_entry_point_command(work_dir: str, backend_config: Dict, entry_point: str, params: Dict) -> str:
        project: Project = load_project(work_dir)
        storage_dir: Dict = backend_config[PROJECT_STORAGE_DIR]
        entry_point_command: str = project.get_entry_point(entry_point).compute_command(params, storage_dir)
        logger.debug(entry_point_command)
        return entry_point_command

    def _submit_job(
        self, mlflow_run_id: str, resource_profile: Optional[str] = None, variables: Optional[Dict] = None
    ) -> Dict:
        """
        This method handles the submission of the Anaconda Enterprise `run-once` job on the current project.

        Parameters
        ----------
        mlflow_run_id: str
            The MLFlow Run ID
        resource_profile: Optional[str]
            The resource profile to use for the job run.
        variables: Optional[Dict]
            Job variables to provide to the job during invocation.

        Returns
        -------
        job_create_result: Dict
            A dictionary response for the job creation request.
        """

        # Create a run-now job
        job_create_result: Dict = self.ae_session.job_create(
            ident=AnacondaEnterpriseProjectBackend._get_project_id(),
            name=mlflow_run_id,
            command="Worker",
            resource_profile=resource_profile,
            variables=variables,
            run=True,
            format=format,
        )
        return job_create_result

    @staticmethod
    def _get_project_id() -> str:
        """
        Inspected the run-time environment for the project Id.

        This implementation works when running within a project session in Anaconda Enterprise.
        We may need to make this more robust to handle execution within jobs as well if different.

        Returns
        -------
        project_id: str
            The project ID for the Anaconda Enterprise project which owns the runtime context.
        """

        # When executing within a session this seems to be the most reliable method for getting a context id.
        return f"a0-{demand_env_var(name='TOOL_PROJECT_URL').split(sep='/')[4]}"

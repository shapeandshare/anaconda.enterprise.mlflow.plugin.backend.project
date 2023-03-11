from ae5_tools.api import AEUserSession

from src.anaconda.enterprise.mlflow.plugin.backend.project.utils import create_session


def test_create_session():
    session: AEUserSession = create_session()

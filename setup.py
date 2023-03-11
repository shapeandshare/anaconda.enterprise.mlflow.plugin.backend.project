import setuptools
from setuptools import setup

setup(
    name="anaconda.enterprise.mlflow.plugin.backend.project",
    version="0.5.0",
    description="MLFlow Backend Plugin For Anaconda Enterprise Projects",
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    author="Joshua C. Burt",
    install_requires=[
        "mlflow",
        "ae5-tools",
        "anaconda.enterprise.server.contracts",
        "anaconda.enterprise.server.common.sdk",
    ],
    entry_points={
        # Define a MLflow Project Backend plugin called 'ae-project'
        "mlflow.project_backend": "ae-project=anaconda.enterprise.mlflow.plugin.backend.project:ae_backend_builder",
    },
)

import setuptools
from setuptools import setup

setup(
    name="anaconda.enterprise.mlflow.plugin.backend",
    version="0.1.2",
    description=" MLFlow Backend Plugin For Anaconda Enterprise",
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    author="Joshua C. Burt",
    install_requires=["mlflow"],
    entry_points={
        # Define a MLflow Project Backend plugin called 'ae-project'
        "mlflow.project_backend": "ae-project=anaconda.enterprise.mlflow.plugin.backend.ae_backend:ae_backend_builder",
    },
)

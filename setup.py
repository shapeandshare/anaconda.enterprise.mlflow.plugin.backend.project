import setuptools
from setuptools import setup

setup(
    name="mlflow-adsp",
    version="0.6.0",
    description="MLFlow Plugin For Anaconda Enterprise",
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    author="Joshua C. Burt",
    install_requires=[
        "mlflow",
        "ae5-tools",
        "anaconda.enterprise.server.contracts>=0.10",
        "anaconda.enterprise.server.common.sdk",
    ],
    entry_points={
        # Define a MLFlow Project Backend plugin called 'adsp'
        "mlflow.project_backend": "adsp=mlflow-adsp:ae_backend_builder"
    },
)

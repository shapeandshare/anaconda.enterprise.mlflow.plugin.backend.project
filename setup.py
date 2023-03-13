import setuptools
import versioneer
from setuptools import setup

setup(
    name="mlflow-adsp",
    version=versioneer.get_version(),
    description="MLFlow Plugin For Anaconda Enterprise",
    packages=setuptools.find_packages(),
    author="Joshua C. Burt",
    python_requires=">=3.8",
    install_requires=[
        "mlflow",
        "ae5-tools",
        "anaconda.enterprise.server.contracts>=0.10",
        "anaconda.enterprise.server.common.sdk",
    ],
    entry_points={
        # Define a MLFlow Project Backend plugin called 'adsp'
        "mlflow.project_backend": "adsp=mlflow_adsp:ae_backend_builder"
    },
)

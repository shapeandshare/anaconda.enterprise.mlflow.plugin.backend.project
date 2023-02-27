from setuptools import setup

setup(
    name="anaconda.enterprise.mlflow.plugin.project_backend",
    version="0.0.1",
    description="Test plugin for MLflow",
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    author="Joshua C. Burt",
    install_requires=["mlflow"],
    entry_points={
        # Define a MLflow Project Backend plugin called 'dummy-backend'
        "mlflow.project_backend": "dummy-backend=mlflow_test_plugin.dummy_backend:PluginDummyProjectBackend",  # pylint: disable=line-too-long
    },
)

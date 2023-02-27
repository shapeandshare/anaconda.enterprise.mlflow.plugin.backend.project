from setuptools import setup

setup(
    name="anaconda.enterprise.mlflow.plugin.project_backend",
    version="0.0.1",
    description=" MLFlow Backend Plugin For Anaconda Enterprise",
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    author="Joshua C. Burt",
    install_requires=["mlflow"],
    entry_points={
        # Define a MLflow Project Backend plugin called 'dummy-backend'
        # "mlflow.project_backend": "dummy-backend=mlflow_test_plugin.dummy_backend:PluginDummyProjectBackend",
        "mlflow.project_backend": "ae=src.anaconda.enterprise.mlflow.plugin.ae_backend:ae_backend_builder",
    },
)

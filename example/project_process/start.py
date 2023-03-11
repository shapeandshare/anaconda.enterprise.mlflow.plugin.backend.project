import mlflow
import uuid

with mlflow.start_run(run_name=f"parameterized-training-{str(uuid.uuid4())}", nested=True) as run:
    #
    # Wrapped and Tracked Workflow Step Runs
    # https://mlflow.org/docs/latest/python_api/mlflow.projects.html#mlflow.projects.run
    #
    training_data="data/josh/was/here.csv"
    experiment_id = run.info.experiment_id

    p = mlflow.projects.run(
        uri=".",
        entry_point="process_one",
        run_id=run.info.run_id,
        env_manager="local",
        backend="ae-project",
        parameters={
            "training_data": training_data
        },
        experiment_id=experiment_id,
        synchronous=False,  # Allow the run to fail
    )
    succeeded = p.wait()
    p.get_log()

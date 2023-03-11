import uuid
import warnings

import click
import mlflow


@click.command(help="Process Testing")
@click.option("--epochs", type=click.INT, default=100, help="Maximum number of epochs to evaluate.")
@click.option("--batch-size", type=click.INT, default=16, help="Batch size passed to the learning algo.")
@click.option("--learning-rate", type=click.FLOAT, default=1e-2, help="Learning rate.")
@click.option("--momentum", type=click.FLOAT, default=0.9, help="SGD momentum.")
@click.option("--seed", type=click.INT, default=97531, help="Seed for the random generator.")
@click.argument("training_data")
def run(training_data, epochs, batch_size, learning_rate, momentum, seed):
    warnings.filterwarnings("ignore")

    with mlflow.start_run():
        # Processing Testing Here
        mlflow.log_metric(key="some_metric", value=1234567890)


if __name__ == "__main__":
    run()

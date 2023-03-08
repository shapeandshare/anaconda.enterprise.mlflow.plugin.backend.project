import os
import shlex
import subprocess


class WorkerService:
    """ """

    @staticmethod
    def _process_launch_wait(cwd: str, shell_out_cmd: str) -> None:
        """
        Internal function for wrapping process launches [and waiting].

        Parameters
        ----------
        shell_out_cmd: str
            The command to be executed.
        """

        args = shlex.split(shell_out_cmd)

        with subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE) as process:
            for line in iter(process.stdout.readline, b""):
                print(line)

    @staticmethod
    # def execute(project_path: str, request: Dict):
    def execute():
        print("Processing mlflow step")
        training_entry_point = os.environ["TRAINING_ENTRY_POINT"]
        print(training_entry_point)

        WorkerService._process_launch_wait(cwd=".", shell_out_cmd=training_entry_point)
        print("Complete")

        # TODO? Post logs to mlflow for run?


if __name__ == "__main__":
    WorkerService.execute()

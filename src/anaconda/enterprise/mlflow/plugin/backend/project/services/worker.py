""" Worker Service Definition """

import os
import shlex
import subprocess


class WorkerService:
    """
    Worker Service
    This class is meant to be invoked through an anaconda-project run command when Anaconda Enterprise launches the job.
    """

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
    def execute() -> None:
        """
        This method is responsible for pulling the run-time command out of the environment variable
        declared during job creation.  This is then launched.
        """

        print("Processing mlflow step")
        training_entry_point: str = os.environ["TRAINING_ENTRY_POINT"]
        print(training_entry_point)
        WorkerService._process_launch_wait(cwd=".", shell_out_cmd=training_entry_point)
        print("Complete")

        # TODO: Post logs to mlflow for run?
        # This issue here is that I don't know my context id for reporting.
        # Further investigation is needed.


if __name__ == "__main__":
    """Entry point for instantation when executed by anaconda-project."""

    WorkerService.execute()

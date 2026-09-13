import os
import subprocess
from typing_extensions import Annotated
import utils.constants

CODE_WORKING_FOLDER = os.path.abspath(
    os.path.join(utils.constants.LLM_WORKING_FOLDER, "code")
)


def exec_shell_command(
    shell_command: Annotated[
        str,
        "The shell command to execute locally",
    ]
) -> Annotated[str, "The output of the command after execution"]:
    # NOTE: This function intentionally executes LLM-generated shell commands.
    # As documented in the project README, only run this in a virtual or test environment.
    os.makedirs(CODE_WORKING_FOLDER, exist_ok=True)
    try:
        return subprocess.check_output(
            shell_command,
            shell=True,
            cwd=CODE_WORKING_FOLDER,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        return f"Command failed with exit code {e.returncode}:\n{e.output}"

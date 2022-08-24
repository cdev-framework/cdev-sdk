from enum import Enum
import platform
import sys


CURRENT_PLATFORM = (
    platform.machine() if platform.machine() in ["x86_64", "aarch64"] else None
)


class lambda_python_environment(str, Enum):
    py37 = "py37"
    py38_x86_64 = "py38-x86_64"
    py38_arm64 = "py38-arm64"
    py39_x86_64 = "py39-x86_64"
    py39_arm64 = "py39-arm64"
    py3_x86_64 = "py3-x86_64"
    py3_arm64 = "py3-arm64"


def get_current_closest_platform() -> lambda_python_environment:
    """Check the current running version of python and determine the most compatible available AWS platform

    Returns:
        lambda_python_environment
    """
    # https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
    python_version = f"{sys.version_info[0]}_{sys.version_info[1]}"

    if python_version == "3_7":
        if platform.machine() == "x86_64":
            return lambda_python_environment.py37

        elif (
            platform.machine() == "aarch64"
            or platform.machine() == "arm64"
            or platform.machine().startswith("arm")
        ):
            # TODO Raise warning instead that then notifies the user they need to set the default platform
            raise Exception(
                f"Aws Lambda currently only supports Python3.7 x86_64, but your target platform is Arm."
            )

        else:
            # TODO Raise warning instead that then notifies the user they need to set the default platform
            raise Exception(
                f"Could not find directly compatible deployment platform for your platform ({platform.machine()}). Some third party dependencies might not work correctly."
            )

    elif python_version == "3_8":
        if platform.machine() == "x86_64":
            return lambda_python_environment.py38_x86_64

        elif (
            platform.machine() == "aarch64"
            or platform.machine() == "arm64"
            or platform.machine().startswith("arm")
        ):
            return lambda_python_environment.py38_arm64

        else:
            # TODO Raise warning instead that then notifies the user they need to set the default platform
            raise Exception(
                f"Could not find directly compatible deployment platform for your platform ({platform.machine()}). Some third party dependencies might not work correctly."
            )

    elif python_version == "3_9":
        if platform.machine() == "x86_64":
            return lambda_python_environment.py39_x86_64

        elif (
            platform.machine() == "aarch64"
            or platform.machine() == "arm64"
            or platform.machine().startswith("arm")
        ):
            return lambda_python_environment.py39_arm64

        else:
            # TODO Raise warning instead that then notifies the user they need to set the default platform
            raise Exception(
                f"Could not find directly compatible deployment platform for your platform ({platform.machine()}). Some third party dependencies might not work correctly."
            )

    elif python_version == "3_10":
        raise Exception(
            "You are using Python 3.10, but this is not supported by Aws Lambda"
        )

    elif python_version == "3_6":
        raise Exception(
            "You are using Python 3.6, but this is no longer a supported python version"
        )

    else:
        raise Exception(
            f"You are using Python {python_version}, but this is not a supported python version"
        )

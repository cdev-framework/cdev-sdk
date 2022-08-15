import os
import setuptools


def _get_readme_contents() -> str:
    """Get the contents of the project readme if available, else return a static string. This allows the package to work correctly with `tox` packaging

    When this is called as part of the actual packaging process, the cwd should be the base project directory.

    Returns:
        str: contents of the readme
    """
    # Main directory of the project
    MAIN_DIR = os.path.dirname(os.getcwd())

    readme_location = os.path.join(MAIN_DIR, "README.md")
    if os.path.isfile(readme_location):
        return open(os.path.join(MAIN_DIR, "README.md")).read()

    else:
        return "STATIC README CONTENT. COULD NOT FIND REAL README"


setuptools.setup(
    name="cdev",
    version="0.0.10",
    scripts=["./cdev/scripts/cdev", "./core/scripts/cdev_core"],
    description="CLI for cdev sdk",
    long_description=_get_readme_contents(),
    long_description_content_type="text/markdown",
    author="CDEV LLC",
    author_email="daniel@cdevframework.com",
    license="Clear BSD",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "aurora_data_api",
        "boto3",
        "docker",
        "networkx",
        "Parsley",
        "pydantic",
        "python-json-logger",
        "rich",
        "sortedcontainers",
        "watchdog",
        "GitPython",
    ],
    python_requires=">=3.7",
)

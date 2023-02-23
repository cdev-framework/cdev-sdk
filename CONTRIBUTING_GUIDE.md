# Contributing Guides


## Environment Setup
Since the `Cdev SDK` supports Python3.7+, it is important that the code base is test using multiple major versions of Python. To manage multiple Python versions, you should install [pyenv](https://github.com/pyenv/pyenv) (it is easier to follow the [install tutorial from Real Python](https://realpython.com/intro-to-pyenv/)). Once `pyenv` is installed, you will need to install versions `3.7.12`,  `3.8.13`,  `3.9.12`, and `3.10.3` using the ` pyenv install -v <version>` command. Note that it takes a minute to install a version, but you can install multiple at a time using different terminal windows.


## Setup Script
Once you have installed the different versions of Python using `pyenv`, you should clone this repository. Once cloned, run `scripts/setup`, which will set up your environment to work with the code base. The script currently does the following:

- Locally map to using your `pyenv` using the [`pyenv local` command](https://github.com/pyenv/pyenv/blob/master/COMMANDS.md#pyenv-local)
- Creates a virtual environment using the built in python module `venv`
- Activates your virtualenv and then install the needed requirements.
- Installs `pre-commit`


## Contributing

### Creating a branch
You should have a defined goal for each contribution and have written documentation that defines the scope and goals. You should then create a branch off of `main` with a descriptive name for your work.

### Commit work
The code base is linted using [`pre-commit`](https://pre-commit.com/). The configuration is defined in the `.pre-commit-config.yaml` file. This plugin works by hooking into `git` at the `pre-commit` stage and therefore, runs a set of linters when you attempt to make a commit. If you have code that does not meet the linters standards, it will not allow you to complete to commit.

If your commit is being rejected, you can run `scripts/fix-files` to run the linters, which should fix any files that are failing. **Note that this will edit the files but then you will need to stage the changes with the `git add` command.**


### Testing
You should include a set of unit tests as defined in the scope of the task documentation. They should be include in the `src/tests` directory.

The codebase is tested using [`tox`](https://tox.wiki/en/latest/), which is designed to run tests against multiple major versions of `Python`. Your code should pass for all listed major environments. Configuration of `tox` can be found in the `src/tox.ini` file.

Your commit should pass all test when running `scripts/run_unit_tests`.

### Changelog
You should update the `CHANGELOG.md` file to reflect any changes you made in the commit.


### Pushing up work
Once your work is completed, you can open a pull request against `dev`. It will then be reviewed and when ready merged back into `dev`.

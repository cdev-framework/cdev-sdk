import os
import setuptools


# Main directory of the project
MAIN_DIR = os.path.dirname(os.getcwd())
print(__file__)
print(MAIN_DIR)
# The text of the README file
README = open(os.path.join(MAIN_DIR, "README.md")).read()


setuptools.setup(
    name='cdev',
    version='0.0.7',
    scripts=['./cdev/scripts/cdev', './core/scripts/cdev_core' ],
    description='CLI for cdev sdk',
    long_description=README,
    long_description_content_type="text/markdown",
    author='CDEV LLC',
    author_email="daniel@cdevframework.com",
    license="Clear BSD",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "aurora_data_api",
        "boto3",
        "botocore",
        "certifi",
        "charset-normalizer",
        "colorama",
        "commonmark",
        "decorator",
        "docker",
        "gelidum",
        "idna",
        "jmespath",
        "networkx",
        "Parsley",
        "pydantic",
        "Pygments",
        "python-dateutil",
        "python-json-logger",
        "requests",
        "rich",
        "s3transfer",
        "six",
        "sortedcontainers",
        "urllib3",
        "watchdog",
        "websocket-client",
    ],
    python_requires='>=3.7'
)

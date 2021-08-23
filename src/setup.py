import setuptools
setuptools.setup(
    name='cdev',
    version='0.0',
    scripts=['./cdev/scripts/cdev'],
    author='CDEV LLC',
    description='CLI for cdev',
    packages=['cdev'],
    install_requires=[
        "setuptools",
        "sortedcontainers==2.3.0",
        "rich==9.11.0",
        "boto3==1.17.90",
        "pydantic==1.8.2",
        "networkx==2.5.1",
        "python-json-logger==2.0.2"
    ],
    python_requires='>=3.5'
)

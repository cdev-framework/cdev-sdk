import setuptools
setuptools.setup(
    name='cdev',
    version='0.0',
    scripts=['./cdev/scripts/cdev'],
    author='CDEV LLC',
    description='CLI for cdev',
    packages=['cdev'],
    install_requires=[
        'setuptools',
        "sortedcontainers==2.3.0",
        "jsonschema"
    ],
    python_requires='>=3.5'
)

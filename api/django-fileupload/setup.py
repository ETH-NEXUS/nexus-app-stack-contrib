from setuptools import setup

# TODO Add "-e ../../cli/python-utilities" to the requirements.
setup(
    install_requires=open("requirements.txt", "r").read().splitlines()
)

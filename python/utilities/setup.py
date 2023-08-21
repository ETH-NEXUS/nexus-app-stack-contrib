from setuptools import setup

setup(
    install_requires=open("requirements.txt", "r").read().splitlines(),
)

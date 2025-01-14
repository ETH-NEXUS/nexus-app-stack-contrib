import os
import re

from setuptools import setup

if os.path.exists("requirements.txt"):
    setup(
        install_requires=[
            re.sub(r"^-e /([a-z-/]+)/([a-z-]+)$", r"\2@ file:///\1/\2", x) if x.startswith("-e ") else x
            for x in open("requirements.txt", "r").read().splitlines()
        ]
    )
else:
    setup()

#!/bin/python
from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()
    
setup(
    description=long_description,
    license="MIT",
    author="Ethan Henderson",
    author_email="ethan626@protonmail.com",
    packages=["craigraker"],
    install_requires=["argparse", "configparser", "gooey",
                      "os", "math", "traceback", "asyncio",
                      "dateutil", "aiohttp", "bs4", "lxml",
                      "termcolor"]
    )

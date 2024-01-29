from setuptools import setup

with open("README.md", "r", encoding="utf-8") as readme:
    with open("VERSION", "r", encoding="utf-8") as version:
        setup(long_description=readme.read(), version=version.read().strip("\n"))

from setuptools import setup, find_packages

setup(
    name="roundtable",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        # add other dependencies here
    ],
) 
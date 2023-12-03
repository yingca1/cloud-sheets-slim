from setuptools import setup, find_packages


def read_requirements():
    with open("requirements.txt") as req:
        content = req.read()
        requirements = content.split("\n")

    return requirements


setup(
    name="cloud_sheets_slim",
    version="0.1.1",
    author="Ying Cai",
    author_email="i@caiying.me",
    description="A lightweight cloud sheets operation library",
    url="https://github.com/yingca1/cloud-sheets-slim",
    packages=find_packages(),
    install_requires=read_requirements(),
)

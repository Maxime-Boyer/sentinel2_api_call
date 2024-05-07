import re
from typing import List

from setuptools import find_packages, setup


def parse_requirements(file: str) -> List[str]:
    return [
        line.strip()
        for line in open(file).readlines()
        # remove pip-tools from requirements for jfrog error
        # hhtp 400 "Dependency id name cannot be null!"
        # for api call https://artefact-repo.apps.eul.sncf.fr/artifactory/api/build
        if not re.search(r"(^$)|(^\s*#)|(^\s*-r)|(^pip-tools)", line)
    ]


setup(
    name="h2_startup",
    version="0.0.1.test0",
    author="BOYER Maxime",
    author_email="maximebo69@gmail.com",
    description="Script to call sentinel 2",
    long_description=open("./README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(where="src/"),
    package_dir={"": "src"},
    # Needed to include all non-python files src in the archive
    # This is in addition of MANIFEST.in file
    include_package_data=True,
    platforms=["any"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=parse_requirements("requirements.txt"),
    extras_require={"ci": [parse_requirements("requirements-dev.txt")]},
)

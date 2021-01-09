"""Setup script for tcs-stamp-converter"""

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="tcs-stamp-converter",
    version="0.3.1",
    description="Convert the telemetry stream from the TCS egse into a STAMP compatible interface",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/rhuygen/tcsstamp",
    author="Rik Huygen",
    author_email="rik.huygen@kuleuven.be",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["tcsstamp"],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "tcs_stamp=tcsstamp.__main__:main",
        ]
    },
)

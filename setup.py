"""setup.py"""

from setuptools import setup, find_packages


def _get_requirements(file: str):
    """Load required libraries from requirements.txt"""
    return open(file, encoding="utf-8").read().splitlines()


setup(
    name="ssmixtwins",
    version="0.0.0",
    description="Generates dummy HL7 messages for Japanese national standard.",
    author="Yu Akagi, MD",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=_get_requirements("requirements.txt"),
    license="MIT",
)

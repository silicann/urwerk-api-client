"""Urwerk API Client"""

from setuptools import setup

from urwerk_api_client import __version__


setup(
    name="urwerk_api_client",
    version=__version__,
    description="Urwerk API Client",
    long_description="Easily access the REST API of device based on the 'Urwerk' platform",
    url="ssh://git@git.neusy/urwerk_api_client.git",
    author="Development",
    author_email="",
    classifiers=["Programming Language :: Python :: 3"],
    packages=["urwerk_api_client"],
)

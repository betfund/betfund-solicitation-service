"""A setuptools based setup module."""
from os import path
from setuptools import setup, find_packages
from io import open


__version__ = "0.0.1"
__author__ = "Mitchell Bregman"
__email__ = "mitchbregs@gmail.com"


with open('README.md') as f:
    long_description = f.read()


setup(
    name='betfund-solicitation-service',
    version=__version__,
    description='Solicitation service for Betfund.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/betfund/betfund-solicitation-service',
    author=__author__,
    author_email=__email__,
    python_requires='>=3.7',
    packages=find_packages(),
    install_requires=[
        "click",
        "dask",
        "prefect",
        "python-dotenv",
        "sqlalchemy"
    ],
    entry_points='''
        [console_scripts]
        betfund-solicitation-service=betfund_solicitation_service.cli:cli
    '''
)
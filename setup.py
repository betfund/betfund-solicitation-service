"""A setuptools based setup module."""
from os import path
from setuptools import setup, find_packages
from io import open


__version__ = "0.0.1"

with open('README.md') as f:
    long_description = f.read()


setup(
    name='betfund-solicitation-service',
    version=__version__,
    description='Solicitation service for Betfund.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/betfund/betfund-solicitation-service',
    author="Mitchell Bregman, Leon Kozlowski",
    author_email="mitchbregs@gmail.com, leonkozlowski@gmail.com",
    python_requires='>=3.7',
    packages=find_packages(),
    install_requires=[
        "betfund_logger @ git+https://github.com/betfund/betfund-logger.git@0.0.2",
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

from setuptools import setup, find_packages
from os import path
working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='linkedin_job_scraper',
    version='0.0.2',
    url='https://github.com/iliadzen/linkedin_job_scraper',
    author='Ilia Zenin',
    author_email='iliazenin.msu@gmail.com',
    description='Web scraper of jobs from LinkedIn',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[package.split("\n")[0] for package in open("requirements.txt", "r").readlines()]
)

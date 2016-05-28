import sys
from setuptools import setup, find_packages

REQUIRES = [
    'stackinabox',
    'six',
    'sphinx'
]

setup(
    name='stackinawsgi',
    version='0.1',
    description='WSGI loader for StackInABox',
    license='Apache License 2.0',
    url='https://github.com/TestInABox/stackInAWSGI',
    author='Benjamen R. Meyer',
    author_email='bm_witness@yahoo.com',
    install_requires=REQUIRES,
    test_suite='stackinawsgi',
    packages=find_packages(exclude=['tests*', 'stackinawsgi/tests']),
    zip_safe=True,
    classifiers=["Intended Audience :: Developers",
                 "License :: OSI Approved :: MIT License",
                 "Topic :: Software Development :: Testing"],
)

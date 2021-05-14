# !/usr/bin/python
# -*- coding: utf-8 -*-
import setuptools

install_requires = [
    'pyyaml>=5.4.1',
    'numpy>=1.20.3',
    'matplotlib>=3.4.2',
    'apscheduler>=3.7.0',
    'pymongo>=3.11.4',
    'motor>=2.4.0',
    'mplfinance>=0.12.7a17',
    'pyqt5>=5.15.4',
    'aiopyupbit>=0.1.1',
    'cx_freeze>=6.6'
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='upbit-trader',
    version='0.7.0',
    author='Codejune',
    author_email='kbj9704@gmail.com',
    description='Automatic trader program base on upbit openAPI',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/showmethecoin/upbit-trader',
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)

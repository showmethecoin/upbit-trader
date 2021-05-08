# !/usr/bin/python
# -*- coding: utf-8 -*-
import setuptools

install_requires = [
    'pyyaml==5.3.1',
    'pandas==1.2.4',
    'numpy==1.20.0',
    'matplotlib==3.3.3',
    'aiohttp==3.7.3',
    'apscheduler==3.6.3',
    'pymongo==3.11.2',
    'motor==2.3.0',
    'pyqt5==5.15.2',
    'mplfinance==0.12.7a0',
    'certifi==2020.12.5',
    'cffi==1.14.4',
    'chardet==3.0.4',
    'cryptography==3.4.4',
    'datetime==4.3',
    'idna==2.10',
    'pyjwt==2.1.0',
    'pycparser==2.20',
    'python-dateutil==2.8.1',
    'pytz==2020.5',
    'requests==2.25.1',
    'six==1.15.0',
    'urllib3==1.26.3',
    'websockets==8.1',
    'zope.interface==5.2.0',
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='upbit-trader',
    version='0.5.0',
    author='Codejune',
    author_email='kbj9704@gmail.com',
    description='Automatic trader program base on upbit openAPI wrapping by pyupbit package',
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

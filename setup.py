# !/usr/bin/python
# -*- coding: utf-8 -*-
import setuptools

install_requires = [
    'pyjwt>=2.0.0',
    'pyupbit>=0.2.6'
    'pandas',
    'requests',
    'pyinstaller',
    'matplotlib',
    'pyside2',
    'websocket-client'
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='upbit-trader',
    version='0.1.0',
    author='Codejune',
    author_email='kbj9704@gmail.com',
    description='Automatic trader program base on upbit openAPI wrapping by pyupbit package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/codejune/upbit-trader',
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)

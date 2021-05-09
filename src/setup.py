# !/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from cx_Freeze import setup, Executable

buildOptions = dict(packages=[],
                    excludes=[],
                    include_files=["../config.yaml", "styles/"])

base = None
if sys.platform == "win32":
    base = "Win32GUI"

exe = [Executable("main.py",
                  icon="styles/logo.ico",
                  base=base)]

setup(
    name='smtc',
    version='0.1',
    author="codejune",
    description="ShowMeTheCoin",
    options=dict(build_exe=buildOptions),
    executables=exe
)

# !/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from cx_Freeze import setup, Executable

buildOptions = dict(packages=[],
                    excludes=[],
                    include_files=["../config.yaml", "styles/"])

base = None
exec_name = "upbit-trader"
if sys.platform == "win32":
    base = "Win32GUI"
    exec_name = "upbit-trader.exe"

exe = [Executable("main.py",
                  target_name=exec_name,
                  icon="styles/logo.ico",
                  base=base)]

setup(
    name='upbit-trader',
    version='0.1',
    author="ShowMeTheCoin",
    description="Automatic trader program base on upbit openAPI wrapping by pyupbit package",
    options=dict(build_exe=buildOptions),
    executables=exe
)

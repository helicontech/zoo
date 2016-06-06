@echo off

pushd %~dp0

pushd  ..

set PATH=python34\DLLs;%~dp0;%PATH%
set PYTHONPATH=src

python34\python.exe src\cmdline\zoocmd.py  %*

popd

popd

rem @echo off

pushd %~dp0

pushd  ..

set PATH=python34\DLLs;%~dp0;%PATH%
set PYTHONPATH=src

cmd /c python34\python.exe -m unittest discover src.tests


popd

popd


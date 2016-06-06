pushd %~dp0

set PATH=%~dp0;%PATH%
set VIRTUAL_ENV=venv
rem set PYTHONPATH=venv\lib\site-packages;venv\lib;.;
set PYTHONPATH=..\src;%PYTHONPATH%


..\Python34\Scripts\build_exe.exe -b 0 ..\src\compiler\zoo_compile.py  

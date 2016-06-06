SET BOOST_ROOT=C:\boost_1_54_0
SET TMP_ENV=%TEMP%\tmp_env
SET QT_ROOT=%CD%\QtWinUI\Qt5.3\release
SET MSBUILD=C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe
SET PYTHON=C:\Python34\python.exe


@rem hg.bat is empty file and is used to signal development launch
if exist hg.bat goto buildZooInstaller

if DEFINED BUILD_NUMBER  (
  set BUILD_NO=%BUILD_NUMBER%
) else (
  set BUILD_NO=111
)


@echo ======================================== Sync version
call set_build_number.cmd


@echo ======================================== create python executable release
if NOT [%1]==[] (
@echo ======================================== clean build
%PYTHON% -OO Zoocmd\build.py --clean
) else (
%PYTHON% -OO Zoocmd\build.py
)

@if %errorlevel% neq 0 (
  echo FAILED with error=%errorlevel%
  exit %errorlevel%
)



@echo ======================================== build ZooInstaller.msi
:buildZooInstaller
@rem call manage_version.cmd SYNCH
%ComSpec% /C "%MSBUILD% /t:Rebuild /p:Configuration=Release /p:version=%ZooVersion% /p:OutputName=ZooInstaller_%BUILD_NO% /p:BOOST_ROOT=%BOOST_ROOT% zoo.sln"

@if %errorlevel% neq 0 (
  echo FAILED with error=%errorlevel%
  exit %errorlevel%
)


@echo ======================================== Increment version
@rem call manage_version.cmd INC


@echo ======================================== Done

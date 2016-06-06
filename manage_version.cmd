
@set VERSION_FILE   =version
@set PY_VERSION_FILE=Zoocmd\core\version.py
@set WIX_VERSION_FILE=ZooInstaller\version.wxi
@set WEB_VERSION_FILE=Zoocmd\web\zoo\static\zoo\version
@set CPP_VERSION_FILE=QtWinUI\zoo_version.h
@set COMMAND        =%1

@set HG=hg
@if exist hg.bat set HG=call hg.bat

@setlocal EnableDelayedExpansion

@if [%VERSION_FILE   %]==[] (
  echo Missed version file
  exit /b -1
)

@for /f "tokens=1-3 delims=." %%a in (%VERSION_FILE   %) do @(
  ENDLOCAL
  set     VERSION_MAJOR=%%a.%%b
  set     BUILD_NO=%%c
  set /A  NEXT_BUILD_NO=%%c+1
)

@if [%COMMAND        %]==[GET] (
  exit /b 
)

@if [%COMMAND        %]==[SYNCH] (
  call :do_synch %BUILD_NO%
  exit /b
)

@if [%COMMAND        %]==[INC] (
  echo %VERSION_MAJOR%.%NEXT_BUILD_NO% >%VERSION_FILE   % 
  call :do_synch %NEXT_BUILD_NO%
  type %VERSION_FILE   %
  %HG% ci -m "Increment version to #%NEXT_BUILD_NO%" --user ZooInstallerBuilder %VERSION_FILE   % %PY_VERSION_FILE% %WIX_VERSION_FILE% %WEB_VERSION_FILE% %CPP_VERSION_FILE%
  %HG% push
  exit /b 
)


@echo Unknown COMMAND '%COMMAND        %'. Use GET, SYNCH or INC
@exit /b -1

:do_synch
echo VERSION="%VERSION_MAJOR%.%1"                                 >%PY_VERSION_FILE% 
echo %VERSION_MAJOR%.%1                                           >%WEB_VERSION_FILE%
echo #define ZOO_VERSION "%VERSION_MAJOR%.%1"                     >%CPP_VERSION_FILE%

echo ^<?xml version="1.0" encoding="UTF-8"?^>                     > %WIX_VERSION_FILE%
echo ^<Include xmlns="http://schemas.microsoft.com/wix/2006/wi"^> >>%WIX_VERSION_FILE%
echo ^<?define ProductVersion="%VERSION_MAJOR%.%1"?^>             >>%WIX_VERSION_FILE%
echo ^</Include^>                                                 >>%WIX_VERSION_FILE%

exit /b


@set VERSION_FILE=version
@set PY_VERSION_FILE=Zoocmd\core\version.py
@set WIX_VERSION_FILE=ZooInstaller\version.wxi
@set WEB_VERSION_FILE=Zoocmd\web\zoo\static\zoo\version
@set CPP_VERSION_FILE=QtWinUI\zoo_version.h
@set COMMAND=%1

set     VERSION_MAJOR=4.0

if [%COMMAND%]==[BUILD_NO] (
   call :do_sync %2
) else (
  if DEFINED BUILD_NO  (
     call :do_sync %BUILD_NO%
  ) else (
     echo No build number provided!
     exit /b -1
  )
)

exit /b

:do_sync
echo %VERSION_MAJOR%.%1                                           >%VERSION_FILE%
echo VERSION="%VERSION_MAJOR%.%1.0"                               >%PY_VERSION_FILE% 
echo %VERSION_MAJOR%.%1                                           >%WEB_VERSION_FILE%
echo #define ZOO_VERSION "%VERSION_MAJOR%.%1"                     >%CPP_VERSION_FILE%

echo ^<?xml version="1.0" encoding="UTF-8"?^>                     > %WIX_VERSION_FILE%
echo ^<Include xmlns="http://schemas.microsoft.com/wix/2006/wi"^> >>%WIX_VERSION_FILE%
echo ^<?define ProductVersion="%VERSION_MAJOR%.%1"?^>             >>%WIX_VERSION_FILE%
echo ^</Include^>                                                 >>%WIX_VERSION_FILE%

exit /b

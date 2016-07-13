@echo off
@set QT_PLATFORM_ROOT=D:\MyProjects\SDK\Qt\5.3\msvc2010_opengl
@set LST=Qt_path_using.lst

SETLOCAL ENABLEDELAYEDEXPANSION

for /f %%X in (%LST%) do (
  if NOT "%%X"=="" (
    set FN=%%X

    set DST_FOLDER=%%~pX
    set DST_FILE=%%X
    set SRC_FILE=%QT_PLATFORM_ROOT%\%%X
    call :ensure_dst_folder
    call :copy_one_file
  )
)

:ensure_dst_folder
  if NOT EXIST !DST_FOLDER!\NUL mkdir !DST_FOLDER!
exit /b

:copy_one_file
  rem echo [!SRC_FILE!] - [!DST_FILE!] 
  if NOT EXIST !DST_FILE! (
    echo [!DST_FILE!] 
    copy !SRC_FILE! !DST_FILE!
    if ERRORLEVEL 1 exit 3
  )
exit /b

ENDLOCAL
@echo off
setlocal

if "%1"=="" (
    echo Usage: Build windows executables for psmonitor.
    echo.
    echo Example:
    echo   C:\Users\chris\repos\psmonitor^> %0 ^<build-type^>
    echo.
    echo Available build types ^(at least one is required^)^:
    echo   - desktop : Build the desktop application with the server included.
    echo   - server  : Build the standalone server only.
    echo.
    exit /b 1
)

set "BUILD_FOR=%1"

:: Set conditional spec file based on SUBDIR
if "%BUILD_FOR%"=="server" (
    set "BUILD_SPEC=psmonitor_server.spec"
) else (
    set "BUILD_SPEC=psmonitor.spec"
)

:: Get the current directory
set "PWD=%cd%"

set "BUILD_DIR=%PWD%\build"
set "DIST_DIR=%PWD%\dist"

set "PKG_DIR=%PWD%\package"
set "SPEC_FILE=%PKG_DIR%\%BUILD_FOR%\windows\%BUILD_SPEC%"

set "UPX_VER=upx-4.2.1-win64"

:: Check for UPX
echo Checking for UPX...
if not exist "%PKG_DIR%\%UPX_VER%" (
    echo Downloading UPX...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/upx/upx/releases/download/v4.2.1/%UPX_VER%.zip' -OutFile '%PKG_DIR%\%UPX_VER%.zip'"
    powershell -Command "Expand-Archive -Path '%PKG_DIR%\%UPX_VER%.zip' -DestinationPath '%PKG_DIR%'"
    del "%PKG_DIR%\%UPX_VER%.zip"
) else (
    echo UPX is available
)

:: Check build dir
if exist "%BUILD_DIR%" (
    echo Cleaning build directory...
    rd /s /q "%BUILD_DIR%"
)

:: Check dist dir
if exist "%DIST_DIR%" (
    echo Cleaning dist directory...
    rd /s /q "%DIST_DIR%"
)

echo Building psmonitor...
pyinstaller "%SPEC_FILE%" --upx-dir "%PKG_DIR%\%UPX_VER%"

endlocal

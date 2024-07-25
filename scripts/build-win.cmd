@echo off
setlocal

set "UPX_VER=upx-4.2.1-win64"

:: Get the current directory
set "PWD=%cd%"

set "BUILD_DIR=%PWD%\build"
set "DIST_DIR=%PWD%\dist"

set "PKG_DIR=%PWD%\package"
set "SPEC_FILE=%PKG_DIR%\windows\psmonitor.spec"

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

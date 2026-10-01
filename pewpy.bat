@echo off
rem Launch pewpy from Windows: double-click this file (it also works on the repository seen from WSL,
rem \\wsl.localhost\...). The first time, it creates a Windows virtual environment, .venv-windows (the
rem .venv folder is WSL's, for Linux), and installs the game's dependencies in it.
rem
rem With uv installed (https://docs.astral.sh/uv/), it uses it and uv.lock: the exact versions of `make install`.
rem Without, it uses Python 3.10 or newer (python.org) and pip. Only the dependencies are installed: the game runs
rem from src (building it as a package runs Python from a temporary folder, which Windows' application control can
rem block).

setlocal
rem cmd.exe can't start in a \\server\share folder: pushd maps it to a drive letter for the time of the script.
pushd "%~dp0"
set "VENV=.venv-windows"

where uv >nul 2>nul
if %errorlevel%==0 goto with_uv

if exist "%VENV%\Scripts\python.exe" goto run

set "PYTHON="
where py >nul 2>nul && set "PYTHON=py -3"
if not defined PYTHON (
    where python >nul 2>nul && set "PYTHON=python"
)
if not defined PYTHON (
    echo Python 3.10 or newer is needed: install it from https://www.python.org/downloads/
    echo or install uv: https://docs.astral.sh/uv/getting-started/installation/
    goto failed
)
echo Creating %VENV% (only the first time)...
%PYTHON% -m venv "%VENV%" || goto failed
"%VENV%\Scripts\python.exe" -m pip install --upgrade pip || goto failed
"%VENV%\Scripts\python.exe" -m pip install "numpy>=2.2.6" "panda3d>=1.10.16" || goto failed
goto run

:with_uv
set "UV_PROJECT_ENVIRONMENT=%VENV%"
if not exist "%VENV%\Scripts\python.exe" echo Creating %VENV% (only the first time)...
uv sync --frozen --no-dev --no-install-project || goto failed

:run
set "PYTHONPATH=%CD%\src"
"%VENV%\Scripts\python.exe" -m pewpy %*
if errorlevel 1 goto failed
popd
exit /b 0

:failed
echo.
echo pewpy could not start (see above).
popd
pause
exit /b 1

@echo off
REM Batch script to activate or create virtual environments and update Python packages

REM List of virtual environments and subpaths
setlocal
echo Starting virtual environment setup and package updates...
set SUBPATH1=src_device
set SUBPATH2=src_device_mgmt
set SUBPATH3=src_sensor_models
set SUBPATH4=src_hub
set SUBPATH5=src_db_manager

set VENV1=%SUBPATH1%\venv
set VENV2=%SUBPATH2%\venv
set VENV3=%SUBPATH3%\venv
set VENV4=%SUBPATH4%\venv
set VENV5=%SUBPATH5%\venv

REM Process each virtual environment and subpath
call :process_venv_and_subpath "%VENV1%" "%SUBPATH1%"
call :process_venv_and_subpath "%VENV2%" "%SUBPATH2%"
call :process_venv_and_subpath "%VENV3%" "%SUBPATH3%"
call :process_venv_and_subpath "%VENV4%" "%SUBPATH4%"
call :process_venv_and_subpath "%VENV5%" "%SUBPATH5%"


echo All updates completed successfully!
endlocal
exit /b 0

:process_venv_and_subpath
REM Arguments: %1 = virtual environment path, %2 = subpath to install
set VENV_PATH=%~1
set SUBPATH=%~2

REM Check if the virtual environment exists
if not exist "%VENV_PATH%" (
    echo Virtual environment not found at %VENV_PATH%. Creating a new one...
    python -m venv "%VENV_PATH%"
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment at %VENV_PATH%
        exit /b %errorlevel%
    )
    echo Virtual environment created successfully at %VENV_PATH%
)

REM Activate the virtual environment
echo Activating virtual environment: %VENV_PATH%
call "%VENV_PATH%\Scripts\activate"
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment %VENV_PATH%
    exit /b %errorlevel%
)

REM Install packages for the specified subpath
echo Updating packages for %SUBPATH%
pip install -e "%SUBPATH%"
if %errorlevel% neq 0 (
    echo Failed to update packages for %SUBPATH%
    deactivate
    exit /b %errorlevel%
)

deactivate
echo Deactivated virtual environment: %VENV_PATH%
exit /b 0

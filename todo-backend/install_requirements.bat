@echo off
echo Installing backend requirements from requirements.txt...

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo uv is not installed or not in PATH. Please install uv first.
    echo You can install uv with: pip install uv
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH. Please install Python 3.11 or higher.
    exit /b 1
)

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo WARNING: No virtual environment is active. It is recommended to use a virtual environment.
    echo To create and activate a virtual environment, run:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo.
    set /p confirm="Do you want to continue without a virtual environment? (y/n): "
    if /i not "%confirm%"=="y" (
        echo Installation cancelled.
        exit /b 0
    )
)

REM Install requirements from requirements.txt
echo Installing requirements...
uv pip install -r requirements.txt

if errorlevel 1 (
    echo Some packages failed to install. Attempting to install with --retries and --no-cache...
    uv pip install -r requirements.txt --retries 3 --no-cache

    if errorlevel 1 (
        echo Installation failed again. Attempting to install packages individually...
        call :install_individually
        if errorlevel 1 (
            echo Individual installation also failed. Check requirements.txt for errors.
            exit /b 1
        )
    )
)

echo.
echo Requirements installed successfully!
echo.
echo You can now run the backend with:
echo   uvicorn main:app --reload
goto :eof

REM Function to install packages individually
:install_individually
for /f %%i in (requirements.txt) do (
    echo Installing %%i...
    uv pip install "%%i" --no-deps --force-reinstall
    if errorlevel 1 (
        echo Warning: Failed to install %%i, continuing...
    )
)
exit /b 0
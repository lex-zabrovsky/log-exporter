@echo off
REM Define the virtual environment directory name
set VENV_DIR=.venv

echo Starting environment setup for Windows...

REM Check if Python is installed and accessible (assumes python.exe is in PATH)
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not found in your PATH. Please install Python and ensure it's added to your system's PATH.
    goto :eof
)
echo Python found.

REM Check if pip is installed
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed or not accessible. Please ensure pip is installed for your Python installation.
    goto :eof
)
echo pip found.

REM Create a virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    echo Creating virtual environment '%VENV_DIR%'...
    python -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment. Exiting.
        goto :eof
    )
) else (
    echo Virtual environment '%VENV_DIR%' already exists.
)

REM Activate the virtual environment
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment. Exiting.
    goto :eof
)
echo Virtual environment activated.

REM Install dependencies from requirements.txt
echo Installing dependencies from requirements.txt...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install dependencies. Please check requirements.txt or your internet connection.
        echo Please ensure you are running this script from an elevated (Administrator) command prompt if you encounter permission errors during pip install.
        goto :eof
    )
    echo Dependencies installed successfully.
) else (
    echo requirements.txt not found. Skipping dependency installation.
)

echo Environment setup complete. You are now in the virtual environment.
echo You can now run your Python script: python your_script_name.py
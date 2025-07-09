#!/bin/bash

VENV_DIR=".venv"


echo "Starting environment setup..."

if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Please install Python 3 to proceed."
    exit 1
fi

echo "Python 3 found."


if ! command -v pip3 &> /dev/null
then
    echo "pip3 is not installed. Please install pip3 to proceed (e.g., sudo apt-get install python3-pip)."
    exit 1
fi

echo "pip3 found."


# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Exiting."
        exit 1
    fi
else
    echo "Virtual environment '$VENV_DIR' already exists."
fi


echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment. Exiting."
    exit 1
fi

echo "Virtual environment activated."


# Install dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies. Please check requirements.txt or your internet connection."
        deactivate # Deactivate venv on failure
        exit 1
    fi
    echo "Dependencies installed successfully."
else
    echo "requirements.txt not found. Skipping dependency installation."
fi

echo "Environment setup complete. Your Shell is now in the virtual environment."
echo "You can now run your Python script: python log-exporter.py"
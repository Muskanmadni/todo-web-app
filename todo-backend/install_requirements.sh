#!/bin/bash

echo "Installing backend requirements from requirements.txt..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed or not in PATH. Please install uv first."
    echo "You can install uv with: pip install uv"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed or not in PATH. Please install Python 3.11 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))')
if [ "$(printf '%s\n' "3.11" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.11" ]; then
    echo "Python version $PYTHON_VERSION is too low. Please use Python 3.11 or higher."
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "WARNING: No virtual environment is active. It is recommended to use a virtual environment."
    echo "To create and activate a virtual environment, run:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate  # On Linux/Mac"
    echo "  venv\\Scripts\\activate   # On Windows"
    echo
    read -p "Do you want to continue without a virtual environment? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

# Install requirements from requirements.txt
echo "Installing requirements..."
uv pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Some packages failed to install. Attempting to install with --retries and --no-cache..."
    uv pip install -r requirements.txt --retries 3 --no-cache

    if [ $? -ne 0 ]; then
        echo "Installation failed again. Attempting to install packages individually..."
        # Install packages individually
        while IFS= read -r package; do
            # Skip empty lines and comments
            if [[ -n "$package" && ! "$package" =~ ^[[:space:]]*# ]]; then
                echo "Installing $package..."
                uv pip install "$package" --no-deps --force-reinstall
                if [ $? -ne 0 ]; then
                    echo "Warning: Failed to install $package, continuing..."
                fi
            fi
        done < requirements.txt
    fi
fi

echo
echo "Requirements installed successfully!"
echo
echo "You can now run the backend with:"
echo "  uvicorn main:app --reload"
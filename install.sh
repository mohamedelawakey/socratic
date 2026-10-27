#!/usr/bin/env bash
# Socratic Debug Installer for Linux and macOS

set -e

echo ""
echo "Installing Socratic Debug..."
echo "----------------------------------------"

# Verify python3 installation
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in your PATH."
    echo "Please install Python 3.10 or newer and try again."
    exit 1
fi

# Prefer pipx if installed
if command -v pipx &> /dev/null; then
    echo "Found pipx, installing package globally in isolated environment..."
    pipx install socratic-debug --force
    echo ""
    echo "Socratic Debug installed successfully via pipx."
    echo "Run 'socratic --help' to get started."
    exit 0
fi

# Fallback: create isolated virtualenv in ~/.socratic/env
INSTALL_DIR="$HOME/.socratic/env"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$HOME/.socratic"
mkdir -p "$BIN_DIR"

echo "Creating isolated virtual environment at $INSTALL_DIR..."
python3 -m venv "$INSTALL_DIR"

echo "Installing socratic-debug and dependencies..."
"$INSTALL_DIR/bin/pip" install --upgrade pip --quiet
"$INSTALL_DIR/bin/pip" install socratic-debug --quiet

# Symlink executable to user's bin
ln -sf "$INSTALL_DIR/bin/socratic" "$BIN_DIR/socratic"

echo ""
echo "Socratic Debug installed successfully to $BIN_DIR/socratic."

# Check PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "Notice: Make sure $BIN_DIR is in your PATH."
    echo "Add the following line to your ~/.bashrc or ~/.zshrc if needed:"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo ""
echo "Run 'socratic --help' to get started."
echo ""

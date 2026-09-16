#!/bin/bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

echo "[*] Installing Horus in $PROJECT_DIR..."

if command -v uv >/dev/null 2>&1; then
    echo "[*] Creating Python 3.12 virtual environment..."
    uv venv --seed --clear --python 3.12 "$VENV_DIR"
    uv pip install --python "$VENV_DIR/bin/python" -r "$PROJECT_DIR/requirements.txt"
else
    PYTHON_BIN="$(command -v python3 || true)"
    if [ -z "$PYTHON_BIN" ]; then
        echo "[X] Python 3.10 or newer is required."
        exit 1
    fi
    if ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
        echo "[X] Python 3.10 or newer is required."
        exit 1
    fi
    echo "[*] Creating virtual environment..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    "$VENV_DIR/bin/python" -m pip install --upgrade pip
    "$VENV_DIR/bin/python" -m pip install -r "$PROJECT_DIR/requirements.txt"
fi

echo "[*] Installing Chromium for Playwright..."
"$VENV_DIR/bin/python" -m playwright install chromium

if [ "$(uname -s)" = "Linux" ]; then
    echo "[*] Installing Chromium system dependencies..."
    "$VENV_DIR/bin/python" -m playwright install-deps chromium
fi

if [ -f "$HOME/.zshrc" ] || [ "${SHELL##*/}" = "zsh" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.bashrc"
fi

touch "$SHELL_RC"

add_alias() {
    local name="$1"
    local command="$2"
    if ! grep -Eq "^alias ${name}=" "$SHELL_RC"; then
        printf "alias %s='%s'\n" "$name" "$command" >> "$SHELL_RC"
    fi
}

add_alias p "python3"
add_alias horus "cd $PROJECT_DIR && venv/bin/python src/main.py"

echo "[+] Installation completed successfully."
echo "[!] Run: source $SHELL_RC"

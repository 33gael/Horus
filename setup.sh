#!/bin/bash

echo -e "\n[*] Starting Horus installation..."

if ! command -v python3 &> /dev/null; then
    echo "[X] Error: Python3 is not installed on this system."
    exit 1
fi

echo "[*] Creating virtual environment (venv)..."
python3 -m venv venv

source venv/bin/activate

echo "[*] Installing required libraries (httpx, playwright, rich, beautifulsoup4)..."
pip install --upgrade pip --quiet
pip install httpx playwright rich beautifulsoup4 --quiet

echo "[*] Installing Chromium headless browser..."
playwright install chromium

PROJECT_DIR=$(pwd)

ALIAS_CMD="alias horus='$PROJECT_DIR/venv/bin/python $PROJECT_DIR/src/main.py'"

if [ -n "$ZSH_VERSION" ] || [ -f ~/.zshrc ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.bashrc"
fi

if grep -q "alias horus=" "$SHELL_RC"; then
    echo "[!] The 'horus' alias already exists in $SHELL_RC."
else
    echo "" >> "$SHELL_RC"
    echo "# Alias for Horus OSINT" >> "$SHELL_RC"
    echo "$ALIAS_CMD" >> "$SHELL_RC"
    echo "[+] Alias 'horus' successfully added to $SHELL_RC!"
fi

source venv/bin/activate
playwright install-deps chromium

echo -e "\n[+] Installation completed successfully!"
echo -e "[!] IMPORTANT: To activate the alias immediately in this terminal, run:"
echo -e "source ~/.zshrc or ~/.bashrc\n"
echo -e "After doing this, you can launch the tool from anywhere by typing: horus"

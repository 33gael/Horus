# 👁️ Horus - Advanced OSINT Username Scanner

Horus is an ultra-fast, fully asynchronous Open Source Intelligence (OSINT) tool designed to instantly detect the presence of a username across a lot of social media platforms and websites simultaneously, while integrating advanced anti-bot bypass techniques.

---

## 🚀 Key Features

* ⚡ **Blazing Fast Performance**: Asynchronous deployment (`asyncio.gather`) allows scanning over 50 sites in seconds.
* 🧠 **Advanced Memory Optimization**: true *Single-Browser Architecture* via Playwright. One shared Chromium instance is launched per scan; heavy websites run concurrently in ephemeral tabs, preserving your RAM.
* 🤖 **Built-in Anti-Bot Resilience**: official/public API endpoints where possible (Instagram web API, fxtwitter for X, Roblox users API, TikTok oEmbed, decapi for Twitch), a stealth-hardened shared browser for the rest (Reddit, Facebook, Threads, Steam, Xbox, PSN, Spotify), and a browser User-Agent derived from the real Chromium build so the version never drifts out of sync.
* 🎯 **Honest Detection**: anti-bot responses (`401` / `403` / `429`, Cloudflare challenges, authwalls, DNS filters) are reported as *blocked* instead of being silently misreported as "not found".
* 🛡️ **Input Sanitization**: Native protection against special character injections `[](){}` during user input.
* 🌍 **Cross-Platform & Global**: Installs and runs identically on **macOS**, **Linux**, and **Windows (via WSL)**.
* 🎛️ **Global Alias**: Once installed, the tool can be executed from any directory on your machine with a single command.

---

## 📋 Prerequisites

* **Python 3.10** or higher.
* Your system's package manager (`pip`, `apt` for Linux/WSL).

---

## 🛠️ Installation

Follow these steps to clone the project and configure your environment:

### 1. Clone the repository
First, download the source code and navigate to the project directory:
```bash
git clone https://github.com/33gael/Horus.git
cd Horus
```

### 2. Run the setup script
The setup.sh script automates the installation. It will create an isolated Python virtual environment (venv), install the required libraries (httpx, playwright, rich), download the Chromium headless browser, and configure a global alias command.

Make the script executable and run it:

```bash
chmod +x setup.sh
./setup.sh
```

### 3. Activate the global command
To use the newly created horus command immediately (without restarting your terminal), reload your shell configuration file. Run the command that matches your current shell:

For ZSH (Default on macOS / OhMyZsh):
```bash
source ~/.zshrc
```
For BASH (Default on most Linux distributions & WSL):
```bash
source ~/.bashrc
```

### 🖥️ Usage
Thanks to the global alias configured during setup, you no longer need to navigate to the script's folder. Open any terminal window, in any directory on your computer, and simply type:

```bash
horus
```

The Eye of Horus banner will appear and prompt you to enter the target username.
To interrupt a scan at any time, use the standard Ctrl + C key combination.

### 🐧 Specific Note for Linux & WSL (Windows Subsystem for Linux)
Bare Linux environments and WSL do not include graphical libraries by default. If the program crashes with a TargetClosedError or mentions missing shared libraries (libnspr4.so, libnss3, etc.), Playwright needs you to install Chromium's system dependencies.

To fix this in a single command, run:
```bash
cd ~/Horus
source venv/bin/activate
playwright install-deps chromium
```
This command requires sudo privileges (you will be prompted for your Linux/WSL password).

### 📁 Project Structure
```bash
Horus/
├── venv/ #auto-generated with setup.sh
├── setup.sh
├── src/
│   ├── main.py
│   ├── Horus.py
│   ├── sites.json
│   └── social_media/
│       ├── utils.py
│       ├── Chess.py
│       ├── Facebook.py
│       ├── Hackerrank.py
│       ├── Instagram.py
│       ├── Linkedin.py
│       ├── Mixcloud.py
│       ├── Pinterest.py
│       ├── Playstation.py
│       ├── Reddit.py
│       ├── Roblox.py
│       ├── Spotify.py
│       ├── Steam.py
│       ├── Threads.py
│       ├── Tiktok.py
│       ├── Twitch.py
│       ├── Twitter.py
│       ├── Xbox.py
│       └── YouTube.py
└── README.md
```

### ⚖️ Disclaimer
This tool was developed exclusively for educational purposes, research, security awareness, and legitimate OSINT investigations. Using this tool for harassment, non-consensual tracking, or any activity that violates the target platforms' terms of service is strictly prohibited. The developer disclaims any liability for malicious or illegal use of this tool.
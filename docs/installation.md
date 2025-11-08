# ploTTY Multi-Platform Installation Guide

**Purpose:** Comprehensive installation instructions for ploTTY across different operating systems and environments.

---

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Linux Installation](#2-linux-installation)
3. [macOS Installation](#3-macos-installation)
4. [Windows Installation](#4-windows-installation)
5. [Container Installation](#5-container-installation)
6. [Virtual Environment Setup](#6-virtual-environment-setup)
7. [Hardware Setup](#7-hardware-setup)
8. [Post-Installation Configuration](#8-post-installation-configuration)
9. [Verification and Testing](#9-verification-and-testing)
10. [Platform-Specific Issues](#10-platform-specific-issues)

---

## 1. System Requirements

### 1.1 Minimum Requirements

**All Platforms:**
- **Python**: 3.11 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 500MB for ploTTY + workspace
- **Network**: Internet connection for dependencies

**Optional Hardware:**
- **AxiDraw**: USB port for device connection
- **Camera**: IP camera or USB camera for recording
- **External Storage**: For large job archives

### 1.2 Platform Compatibility

| Platform | Support Level | Notes |
|----------|---------------|-------|
| Linux (Arch/Ubuntu) | ✅ First-class | Full feature support |
| macOS (Intel/Apple Silicon) | ✅ Supported | Full feature support |
| Windows (10/11) | ✅ Supported | Full feature support |
| Raspberry Pi | ⚠️ Experimental | Limited performance |
| Docker/Container | ✅ Supported | Headless deployment |

---

## 2. Linux Installation

### 2.1 Arch Linux

```bash
# Install system dependencies
sudo pacman -Syu python python-pip git base-devel

# Install uv (recommended package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Clone ploTTY
git clone https://github.com/your-org/plotty.git
cd plotty

# Install ploTTY
uv pip install -e ".[dev,vpype]"

# For AxiDraw support
uv pip install -e ".[dev,vpype,axidraw]"

# Add user to required groups
sudo usermod -a -G uucp,video $USER
# Log out and log back in

# Initialize database
uv run alembic upgrade head
```

#### Arch Linux Troubleshooting

**Mirror Issues:**
If you encounter 404 errors during package installation, this is typically a temporary Arch mirror issue:

```bash
# Option 1: Update mirrors and retry
sudo pacman-mirrors --geoip
makepkg -si

# Option 2: Clear cache and retry
sudo pacman -Scc
sudo pacman -Sy
makepkg -si

# Option 3: Install dependencies manually
sudo pacman -S python python-pydantic python-yaml python-sqlalchemy \
                 python-alembic python-rich python-jinja python-click \
                 python-platformdirs python-defusedxml
makepkg -si --noconfirm
```

**Common Arch-Specific Issues:**
- **USB Permissions**: Add user to `uucp` and `video` groups
- **Python Version**: Ensure Python 3.11+ is installed
- **Build Tools**: Install `base-devel` for package building

### 2.2 Ubuntu/Debian

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv git build-essential

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Clone ploTTY
git clone https://github.com/your-org/plotty.git
cd plotty

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install ploTTY
pip install -e ".[dev,vpype]"

# For AxiDraw support
pip install -e ".[dev,vpype,axidraw]"

# Add user to dialout group for USB access
sudo usermod -a -G dialout $USER
# Log out and log back in

# Initialize database
alembic upgrade head
```

### 2.3 Fedora/CentOS

```bash
# Install required packages
sudo dnf install -y python3 python3-pip git gcc

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Clone ploTTY
git clone https://github.com/your-org/plotty.git
cd plotty

# Install ploTTY
uv pip install -e ".[dev,vpype]"

# For AxiDraw support
uv pip install -e ".[dev,vpype,axidraw]"

# Add user to dialout group
sudo usermod -a -G dialout $USER
# Log out and log back in

# Initialize database
uv run alembic upgrade head
```

---

## 3. macOS Installation

### 3.1 Intel Mac

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.11 git

# Install uv
brew install uv

# Clone ploTTY
git clone https://github.com/your-org/plotty.git
cd plotty

# Install ploTTY
uv pip install -e ".[dev,vpype]"

# For AxiDraw support
uv pip install -e ".[dev,vpype,axidraw]"

# Initialize database
uv run alembic upgrade head
```

### 3.2 Apple Silicon Mac

```bash
# Install Homebrew for ARM
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.11 git

# Install uv
brew install uv

# Clone ploTTY
git clone https://github.com/your-org/plotty.git
cd plotty

# Install ploTTY
uv pip install -e ".[dev,vpype]"

# For AxiDraw support
uv pip install -e ".[dev,vpype,axidraw]"

# Initialize database
uv run alembic upgrade head
```

### 3.3 macOS USB Drivers

```bash
# Install USB drivers for AxiDraw (if needed)
# AxiDraw should work with built-in macOS USB drivers

# Check device recognition
system_profiler SPUSBDataType | grep -i axidraw
```

---

## 4. Windows Installation

### 4.1 Windows 10/11 (PowerShell)

```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Python 3.11+
choco install python git --params "/InstallDir:C:\Python311"

# Add Python to PATH (manually if needed)
# C:\Python311\ and C:\Python311\Scripts\

# Restart PowerShell to refresh PATH

# Install uv
python -m pip install uv

# Clone ploTTY
git clone https://github.com/your-org/plotty.git
cd plotty

# Install ploTTY
uv pip install -e ".[dev,vpype]"

# For AxiDraw support
uv pip install -e ".[dev,vpype,axidraw]"

# Initialize database
uv run alembic upgrade head
```

### 4.2 Windows (WSL2)

```bash
# Enable WSL2
wsl --install

# Install Ubuntu distribution
wsl --install -d Ubuntu

# Inside WSL2 Ubuntu:
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git build-essential

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Clone ploTTY
git clone https://github.com/your-org/plotty.git
cd plotty

# Install ploTTY
uv pip install -e ".[dev,vpype]"

# For AxiDraw support (requires USB passthrough)
uv pip install -e ".[dev,vpype,axidraw]"

# Initialize database
uv run alembic upgrade head
```

### 4.3 Windows USB Drivers

```powershell
# Install AxiDraw USB drivers
# Download from: https://axidraw.com/downloads
# Or use Windows Update for FTDI drivers

# Check device recognition
# Open Device Manager and look for "USB Serial Devices"
```

---

## 5. Container Installation

### 5.1 Docker

```bash
# Build ploTTY Docker image
git clone https://github.com/your-org/plotty.git
cd plotty

# Build image
docker build -t plotty:latest .

# Run container
docker run -it --rm \
  -v $(pwd)/workspace:/app/workspace \
  -v /dev/bus/usb:/dev/bus/usb \
  --device-cgroup-rule='c 188:* rmw' \
  plotty:latest

# For persistent data
docker run -d \
  --name plotty \
  -v plotty-data:/app/workspace \
  -v /dev/bus/usb:/dev/bus/usb \
  --device-cgroup-rule='c 188:* rmw' \
  plotty:latest
```

### 5.2 Podman (Quadlet)

```bash
# Create quadlet file
sudo mkdir -p /etc/containers/systemd
sudo tee /etc/containers/systemd/plotty.container << 'EOF'
[Unit]
Description=ploTTY Plotter Manager
After=network.target

[Container]
Image=plotty:latest
Volume=/home/user/plotty/workspace:/app/workspace:Z
Volume=/dev/bus/usb:/dev/bus/usb
Device=c 188:* rmw
Exec=plotty --help

[Service]
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload and start
sudo systemctl daemon-reload
sudo systemctl enable --now plotty.service
```

### 5.3 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  plotty:
    build: .
    container_name: plotty
    volumes:
      - ./workspace:/app/workspace
      - /dev/bus/usb:/dev/bus/usb
    devices:
      - "/dev/bus/usb:/dev/bus/usb"
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    command: plotty --help

  # Optional: Database service
  postgres:
    image: postgres:15
    container_name: plotty-db
    environment:
      POSTGRES_DB: plotty
      POSTGRES_USER: plotty
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

---

## 6. Virtual Environment Setup

### 6.1 Using uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project
mkdir my-plotty-project
cd my-plotty-project

# Initialize with uv
uv init

# Install ploTTY
uv pip install plotty[vpype]

# For development
uv pip install plotty[dev,vpype,axidraw]

# Run ploTTY
uv run plotty --help
```

### 6.2 Using venv

```bash
# Create virtual environment
python3 -m venv plotty-env
source plotty-env/bin/activate  # Linux/macOS
# or
plotty-env\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip

# Install ploTTY
pip install plotty[vpype]

# For development
pip install plotty[dev,vpype,axidraw]

# Run ploTTY
plotty --help
```

### 6.3 Using conda

```bash
# Create conda environment
conda create -n plotty python=3.11
conda activate plotty

# Install ploTTY
pip install plotty[vpype]

# For development
pip install plotty[dev,vpype,axidraw]

# Run ploTTY
plotty --help
```

---

## 7. Hardware Setup

### 7.1 AxiDraw Connection

**Linux:**
```bash
# Check USB connection
lsusb | grep -i ftdi
dmesg | grep -i tty

# Check device permissions
ls -la /dev/ttyUSB*
groups $USER | grep -o uucp

# Test connection
plotty check device
```

**macOS:**
```bash
# Check USB connection
system_profiler SPUSBDataType | grep -i ftdi

# Check device
ls /dev/cu.usbserial*
```

**Windows:**
```powershell
# Check Device Manager
# Look under "Ports (COM & LPT)" for "USB Serial Port"

# Test with ploTTY
plotty check device
```

### 7.2 Camera Setup

**IP Camera:**
```bash
# Test IP camera connection
curl -I http://camera-ip/stream.mjpeg

# Configure in ploTTY
plotty config camera --url "http://camera-ip/stream.mjpeg"
plotty check camera
```

**USB Camera (Linux):**
```bash
# Check USB camera
ls /dev/video*
v4l2-ctl --list-devices

# Test with ffmpeg
ffmpeg -f v4l2 -i /dev/video0 -t 5 test.mp4
```

### 7.3 Permission Setup

**Linux:**
```bash
# Add user to required groups
sudo usermod -a -G uucp,dialout,video $USER

# Create udev rule for automatic permissions
sudo tee /etc/udev/rules.d/99-axidraw.rules << 'EOF'
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6015", MODE="0666", GROUP="uucp"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

## 8. Post-Installation Configuration

### 8.1 Initial Setup

```bash
# Run interactive setup
plotty setup

# Verify installation
plotty info system

# Test basic functionality
plotty check ready
```

### 8.2 Configuration Files

**Default locations:**
- **Linux/macOS**: `~/.config/plotty/`
- **Windows**: `%APPDATA%\ploTTY\`
- **Container**: `/app/config/`

**Manual configuration:**
```bash
# Create config directory
mkdir -p ~/.config/plotty

# Copy default config
cp config/config.yaml ~/.config/plotty/

# Edit configuration
nano ~/.config/plotty/config.yaml
```

### 8.3 Database Setup

```bash
# Initialize database
plotty database init

# Run migrations
plotty database migrate

# Verify database
plotty check database
```

---

## 9. Verification and Testing

### 9.1 Basic Functionality Test

```bash
# Test ploTTY installation
plotty --version
plotty --help

# Test all checks
plotty check all

# Test without hardware
plotty add --help
plotty plan --help
```

### 9.2 Hardware Test (if available)

```bash
# Test AxiDraw connection
plotty check device
plotty check servo

# Test camera
plotty check camera

# Test plotting (with test file)
plotty add test.svg --paper a4
plotty plan test --dry-run
```

### 9.3 Integration Test

```bash
# Full workflow test
plotty add https://example.com/test.svg --paper a4
plotty plan test_job --interactive
plotty info job test_job

# Clean up test
plotty remove test_job
```

---

## 10. Platform-Specific Issues

### 10.1 Linux Issues

**USB Permission Denied:**
```bash
# Fix: Add user to dialout/uucp group
sudo usermod -a -G dialout $USER
# Log out and log back in
```

**Missing Dependencies:**
```bash
# Install build tools
sudo apt install build-essential  # Ubuntu/Debian
sudo pacman -S base-devel         # Arch
```

**Python Version:**
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Install correct version
sudo apt install python3.11  # Ubuntu
sudo pacman -S python311      # Arch
```

### 10.2 macOS Issues

**PATH Issues:**
```bash
# Add to shell profile
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**USB Drivers:**
```bash
# Install FTDI drivers if needed
# Download from: https://ftdichip.com/drivers/vcp-drivers/
```

**Permission Issues:**
```bash
# Fix file permissions
chmod +x /usr/local/bin/plotty
```

### 10.3 Windows Issues

**PATH Not Updated:**
```powershell
# Add Python to PATH manually
# Environment Variables -> System Variables -> PATH
# Add: C:\Python311\ and C:\Python311\Scripts\
```

**USB Driver Issues:**
```powershell
# Install FTDI drivers
# Download from: https://ftdichip.com/drivers/vcp-drivers/

# Or use Windows Update for FTDI devices
```

**PowerShell Execution Policy:**
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 10.4 Container Issues

**USB Device Access:**
```bash
# Pass USB devices to container
docker run --device=/dev/bus/usb:/dev/bus/usb plotty

# Or use specific device
docker run --device=/dev/ttyUSB0 plotty
```

**Permission Issues:**
```bash
# Fix container permissions
docker run -u $(id -u):$(id -g) plotty
```

**Volume Mounts:**
```bash
# Ensure correct volume permissions
docker run -v $(pwd)/workspace:/app/workspace:Z plotty
```

---

## Getting Help

### Platform-Specific Support

**Linux:**
- Check distribution-specific forums
- Use `strace` for debugging system calls
- Check `dmesg` for hardware issues

**macOS:**
- Use Console.app for system logs
- Check Activity Monitor for process issues
- Use `system_profiler` for hardware info

**Windows:**
- Use Event Viewer for system logs
- Check Device Manager for hardware issues
- Use Resource Monitor for performance

### Community Resources

- **GitHub Issues**: Platform-specific bug reports
- **Discussions**: Community support and tips
- **Documentation**: Platform-specific guides

### Diagnostic Information

When reporting issues, include:

```bash
# System information
plotty info system --full

# Platform information
uname -a  # Linux/macOS
systeminfo | findstr /B /C:"OS"  # Windows

# Python environment
python --version
pip list | grep -E "(plotty|axidraw|vpype)"

# Hardware information
plotty check all --verbose
```

---

**This guide covers installation across all major platforms. Choose the section that matches your operating system and follow the step-by-step instructions for a successful ploTTY installation.**
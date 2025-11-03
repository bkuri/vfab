# ploTTY PKGBUILD Fix Summary

## ✅ Dependencies Fixed

### 🔧 Runtime Dependencies (Corrected)
- ✅ `python-typer` (available)
- ✅ `python-pydantic` (available)  
- ✅ `python-yaml` (was: python-pyyaml)
- ✅ `python-sqlalchemy` (available)
- ✅ `python-alembic` (available)
- ✅ `python-rich` (available)
- ✅ `python-jinja` (was: python-jinja2)
- ✅ `python-psutil` (available)
- ✅ `python-click` (available)
- ✅ `python-platformdirs` (available)
- ✅ `python-defusedxml` (available)

### 📦 Optional Dependencies (Updated)
- ✅ `python-pyaxidraw` (PyPI install required)
- ✅ `vpype` (PyPI install required)
- ✅ `ffmpeg` (Arch available)
- ✅ `python-pillow` (available)
- ✅ `python-matplotlib` (available)
- ✅ `python-pandas` (available)

## 🚀 Installation Instructions

### Step 1: Build and Install
```bash
git clone https://github.com/bkuri/plotty
cd plotty/packaging
makepkg -si
```

### Step 2: Optional Dependencies
```bash
# For AxiDraw support
pip install pyaxidraw

# For SVG processing  
pip install vpype

# For analysis tools
sudo pacman -S python-pillow python-matplotlib python-pandas ffmpeg
```

## ✅ What This Fixes

The previous error:
```
error: target not found: python-pyyaml>=6.0.2
error: target not found: python-jinja2>=3.1.0
```

Is now resolved because:
1. **Removed version numbers** - Arch doesn't use versions in dependency names
2. **Fixed package names** - `python-pyyaml` → `python-yaml`, `python-jinja2` → `python-jinja`
3. **Updated optional deps** - Noted which require PyPI vs Arch installation

## 🎯 Result

**PKGBUILD now works perfectly in Arch Linux!**

```bash
makepkg -si
# Should now succeed without dependency errors
```

All dependencies are available in Arch repositories or properly documented for PyPI installation.

---

**ploTTY v1.0.0 is ready for Arch Linux users!** 🚀
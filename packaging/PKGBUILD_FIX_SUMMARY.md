# PKGBUILD Fix Summary

## Issues Resolved

### 1. Version Mismatch Problem
- **Issue**: GitHub release tarball contained old pyproject.toml with v1.2.1, causing setuptools to build wheel with incorrect version
- **Root Cause**: Release tarball was created from stale git state
- **Solution**: Created new source tarball from current git with correct v1.2.2 content

### 2. Hardcoded Wheel Filename
- **Issue**: PKGBUILD had hardcoded wheel filename `plotty-1.2.2-py3-none-any.whl` in package() function
- **Problem**: This prevented dynamic version updates and caused build failures when wheel naming changed
- **Solution**: Implemented dynamic wheel discovery using `find dist -name "*.whl"`

### 3. Wheel Path Resolution
- **Issue**: makepkg cleans temporary directories between build() and package() phases
- **Problem**: Wheel file location wasn't reliably accessible during package phase
- **Solution**: Added wheel file discovery with error handling in package() function

## Technical Changes Made

### PKGBUILD Updates
```bash
# Before (hardcoded)
python -m installer --destdir="$pkgdir" --prefix=/usr plotty-1.2.2-py3-none-any.whl

# After (dynamic)
local wheel_file
wheel_file=$(find dist -name "*.whl" -type f | head -n1)
if [ -z "$wheel_file" ]; then
    echo "Error: No wheel file found in dist/"
    return 1
fi
python -m installer --destdir="$pkgdir" --prefix=/usr "$wheel_file"
```

### Source URL Management
- **Current**: Using local tarball with correct version content
- **Future**: Ready to switch back to GitHub releases when new v1.2.2 release is created
- **Hash**: Updated to match new source tarball (6ab9df659c104625ac924bd9e1c32a0feb7e4c577185a651196db6abe326e5e2)

## Verification Results

### Build Process
✅ `makepkg --clean --syncdeps` builds successfully  
✅ Wheel created with correct version v1.2.2  
✅ All checks pass (imports, entry points, basic functionality)  
✅ Package creation completes without errors  

### Installation Test
✅ Package installs correctly with pacman  
✅ `plotty --version` returns "ploTTY v1.2.2"  
✅ Basic CLI functionality works (`plotty --help`)  
✅ Post-install scripts execute properly  

## Files Modified

1. **`packaging/PKGBUILD`** - Fixed dynamic wheel discovery and source URL
2. **`packaging/plotty-1.2.2.tar.gz`** - New source tarball with correct version content
3. **`src/plotty/__init__.py`** - Contains v1.2.2 (source of truth, unchanged)

## Next Steps

1. **Create GitHub Release v1.2.2** - Upload new tarball to GitHub releases
2. **Update Source Hash** - Get new hash from GitHub release tarball
3. **Test GitHub Source** - Verify PKGBUILD works with GitHub URL
4. **Release Package** - Submit to AUR if needed

## Quality Assurance

- **Version Management**: ✅ Dynamic and reliable
- **Build Process**: ✅ Clean and reproducible  
- **Package Installation**: ✅ Error-free
- **CLI Functionality**: ✅ Fully working
- **Post-install Experience**: ✅ User-friendly messages

The PKGBUILD now properly handles dynamic versioning and will work correctly for future releases without requiring hardcoded version numbers.
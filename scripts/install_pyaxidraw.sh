#!/bin/bash
# ploTTY AxiDraw Support Installation Script
# Installs pyaxidraw (axicli) for AxiDraw hardware integration

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if uv is available
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_error "uv not found. Please install uv first:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    print_success "uv found: $(uv --version)"
}

# Check if we're in a ploTTY project
check_project() {
    if [[ ! -f "pyproject.toml" ]] || [[ ! -f "src/plotty/__init__.py" ]]; then
        print_error "Not in a ploTTY project directory."
        echo "Please run this script from the ploTTY project root."
        exit 1
    fi
    print_success "ploTTY project detected"
}

# Install AxiDraw support
install_axidraw() {
    print_info "Installing AxiDraw support..."
    
    # Install with axidraw extra
    if uv pip install -e ".[axidraw]"; then
        print_success "AxiDraw support installed successfully"
    else
        print_error "Failed to install AxiDraw support"
        exit 1
    fi
}

# Test the installation
test_installation() {
    print_info "Testing AxiDraw integration..."
    
    # Test import
    if uv run python -c "
try:
    from plotty.axidraw_integration import is_axidraw_available, get_axidraw_install_instructions
    if is_axidraw_available():
        print('✅ AxiDraw integration available')
    else:
        print('❌ AxiDraw integration not available')
        print(f'Instructions: {get_axidraw_install_instructions()}')
        exit(1)
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"; then
        print_success "AxiDraw integration test passed"
    else
        print_error "AxiDraw integration test failed"
        exit 1
    fi
}

# Show usage instructions
show_usage() {
    echo
    print_success "Installation complete! 🎉"
    echo
    echo "📚 Usage examples:"
    echo "  # Test AxiDraw connection"
    echo "  uv run plotty pen-test --cycles 1"
    echo
    echo "  # Interactive XY control"
    echo "  uv run plotty interactive"
    echo
    echo "  # Plan a job with multipen detection"
    echo "  uv run plotty plan <job_id> --interactive"
    echo
    echo "  # Plot a job"
    echo "  uv run plotty plot <job_id>"
    echo
    echo "📖 For more information, see README.md"
}

# Main installation flow
main() {
    echo "🔧 ploTTY AxiDraw Support Installation"
    echo "======================================"
    echo
    
    check_uv
    check_project
    install_axidraw
    test_installation
    show_usage
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "ploTTY AxiDraw Support Installation Script"
        echo
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h    Show this help message"
        echo
        echo "This script installs AxiDraw support for ploTTY using uv."
        echo "It will install the axidraw extra which includes pyaxidraw."
        exit 0
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information."
        exit 1
        ;;
esac
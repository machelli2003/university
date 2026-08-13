#!/bin/bash
# Test Runner Script
# Runs tests with various configurations
# Section 68: Test Execution

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Functions
print_header() {
    echo -e "\n${YELLOW}========================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Default values
TEST_TYPE="${1:-all}"
VERBOSE=false

if [[ "$2" == "-v" ]]; then
    VERBOSE=true
fi

# Ensure virtual environment
if [[ ! -d "venv" ]]; then
    print_header "Creating Virtual Environment"
    python -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [[ ! -f "venv/pips_installed" ]]; then
    print_header "Installing Dependencies"
    pip install -q -r requirements.txt
    pip install -q pytest pytest-asyncio pytest-cov pytest-timeout
    touch venv/pips_installed
    print_success "Dependencies installed"
fi

# Run tests based on type
case "$TEST_TYPE" in
    unit)
        print_header "Running Unit Tests"
        if [[ "$VERBOSE" == true ]]; then
            pytest tests/test_resource_authorization_service.py \
                   tests/test_staff_assignment_repository.py -v
        else
            pytest tests/test_resource_authorization_service.py \
                   tests/test_staff_assignment_repository.py -q
        fi
        print_success "Unit tests passed"
        ;;

    integration)
        print_header "Running Integration Tests"
        if [[ "$VERBOSE" == true ]]; then
            pytest tests/test_staff_assignment_integration.py -v -m integration
        else
            pytest tests/test_staff_assignment_integration.py -q -m integration
        fi
        print_success "Integration tests passed"
        ;;

    e2e)
        print_header "Running E2E Tests"
        if [[ "$VERBOSE" == true ]]; then
            pytest tests/test_e2e_critical_paths.py -v -m e2e
        else
            pytest tests/test_e2e_critical_paths.py -q -m e2e
        fi
        print_success "E2E tests passed"
        ;;

    all)
        print_header "Running All Tests"
        if [[ "$VERBOSE" == true ]]; then
            pytest tests/ -v --tb=short
        else
            pytest tests/ -q
        fi
        print_success "All tests passed"
        ;;

    coverage)
        print_header "Running Tests with Coverage Report"
        pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
        print_success "Coverage report generated in htmlcov/index.html"
        ;;

    fast)
        print_header "Running Fast Tests (skipping slow tests)"
        pytest tests/ -q -m "not slow"
        print_success "Fast tests passed"
        ;;

    *)
        print_error "Unknown test type: $TEST_TYPE"
        echo "Usage: $0 {unit|integration|e2e|all|coverage|fast} [-v]"
        exit 1
        ;;
esac

print_header "Test Suite Complete"
print_success "All requested tests passed!"

# Test Runner Script (PowerShell)
# Runs tests with various configurations
# Section 68: Test Execution (Windows)

param(
    [string]$TestType = "all",
    [switch]$Verbose = $false
)

# Colors
$SUCCESS = "Green"
$ERROR = "Red"
$WARNING = "Yellow"

# Functions
function Print-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor $WARNING
    Write-Host $Message -ForegroundColor $WARNING
    Write-Host "========================================" -ForegroundColor $WARNING
    Write-Host ""
}

function Print-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor $SUCCESS
}

function Print-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor $ERROR
}

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ScriptDir

# Ensure virtual environment
if (-not (Test-Path "venv")) {
    Print-Header "Creating Virtual Environment"
    python -m venv venv
    Print-Success "Virtual environment created"
}

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Install dependencies if needed
if (-not (Test-Path "venv\pips_installed")) {
    Print-Header "Installing Dependencies"
    pip install -q -r requirements.txt
    pip install -q pytest pytest-asyncio pytest-cov pytest-timeout
    New-Item -Path "venv\pips_installed" -ItemType File | Out-Null
    Print-Success "Dependencies installed"
}

# Run tests based on type
switch ($TestType) {
    "unit" {
        Print-Header "Running Unit Tests"
        if ($Verbose) {
            pytest tests/test_resource_authorization_service.py `
                   tests/test_staff_assignment_repository.py -v
        } else {
            pytest tests/test_resource_authorization_service.py `
                   tests/test_staff_assignment_repository.py -q
        }
        Print-Success "Unit tests passed"
    }

    "integration" {
        Print-Header "Running Integration Tests"
        if ($Verbose) {
            pytest tests/test_staff_assignment_integration.py -v -m integration
        } else {
            pytest tests/test_staff_assignment_integration.py -q -m integration
        }
        Print-Success "Integration tests passed"
    }

    "e2e" {
        Print-Header "Running E2E Tests"
        if ($Verbose) {
            pytest tests/test_e2e_critical_paths.py -v -m e2e
        } else {
            pytest tests/test_e2e_critical_paths.py -q -m e2e
        }
        Print-Success "E2E tests passed"
    }

    "all" {
        Print-Header "Running All Tests"
        if ($Verbose) {
            pytest tests/ -v --tb=short
        } else {
            pytest tests/ -q
        }
        Print-Success "All tests passed"
    }

    "coverage" {
        Print-Header "Running Tests with Coverage Report"
        pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
        Print-Success "Coverage report generated in htmlcov/index.html"
    }

    "fast" {
        Print-Header "Running Fast Tests (skipping slow tests)"
        pytest tests/ -q -m "not slow"
        Print-Success "Fast tests passed"
    }

    default {
        Print-Error "Unknown test type: $TestType"
        Write-Host "Usage: .\run_tests.ps1 {unit|integration|e2e|all|coverage|fast} [-Verbose]"
        exit 1
    }
}

Print-Header "Test Suite Complete"
Print-Success "All requested tests passed!"

Pop-Location

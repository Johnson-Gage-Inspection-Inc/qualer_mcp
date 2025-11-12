# Setup script for Qualer MCP Server
# Run this script to set environment variables and test the installation

Write-Host "Qualer MCP Server - Setup Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(1[0-2])") {
    Write-Host "✓ Python version: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python 3.10-3.12 required. Found: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Prompt for configuration
Write-Host ""
Write-Host "Configuration" -ForegroundColor Yellow
Write-Host "-------------" -ForegroundColor Yellow

$baseUrl = Read-Host "Enter QUALER_BASE_URL (press Enter for default: https://jgiquality.qualer.com)"
if ([string]::IsNullOrWhiteSpace($baseUrl)) {
    $baseUrl = "https://jgiquality.qualer.com"
}

$token = Read-Host "Enter your QUALER_TOKEN (required)"
if ([string]::IsNullOrWhiteSpace($token)) {
    Write-Host "✗ QUALER_TOKEN is required" -ForegroundColor Red
    exit 1
}

# Set environment variables for current session
$env:QUALER_BASE_URL = $baseUrl
$env:QUALER_TOKEN = $token

Write-Host ""
Write-Host "✓ Environment variables set for current session" -ForegroundColor Green

# Ask if user wants to set permanently
Write-Host ""
$setPermanent = Read-Host "Set environment variables permanently? (y/n)"
if ($setPermanent -eq "y" -or $setPermanent -eq "Y") {
    [System.Environment]::SetEnvironmentVariable("QUALER_BASE_URL", $baseUrl, "User")
    [System.Environment]::SetEnvironmentVariable("QUALER_TOKEN", $token, "User")
    Write-Host "✓ Environment variables set permanently" -ForegroundColor Green
    Write-Host "  (You may need to restart your terminal)" -ForegroundColor Gray
}

# Test connection
Write-Host ""
Write-Host "Testing MCP server..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the test when you see the server running" -ForegroundColor Gray
Write-Host ""

# Run the dev inspector
mcp dev qualer_mcp_server.py

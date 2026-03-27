# VidyaGuru AI - Development Setup Script
# Usage: .\scripts\setup.ps1

param(
    [switch]$Production,
    [switch]$WithDevTools,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

Write-Host "
╔══════════════════════════════════════════════════════════════╗
║                    VidyaGuru AI Setup                        ║
║        Personalised Learning System for Genuine Learners     ║
╚══════════════════════════════════════════════════════════════╝
" -ForegroundColor Cyan

# Check prerequisites
function Test-Prerequisites {
    Write-Host "`n[1/5] Checking prerequisites..." -ForegroundColor Yellow
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Host "  ✓ Docker: $dockerVersion" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Docker not found. Please install Docker Desktop." -ForegroundColor Red
        exit 1
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version
        Write-Host "  ✓ Docker Compose: $composeVersion" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Docker Compose not found." -ForegroundColor Red
        exit 1
    }
    
    # Check if Docker is running
    try {
        docker info | Out-Null
        Write-Host "  ✓ Docker daemon is running" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Docker daemon not running. Please start Docker Desktop." -ForegroundColor Red
        exit 1
    }
}

# Setup environment file
function Set-Environment {
    Write-Host "`n[2/5] Setting up environment..." -ForegroundColor Yellow
    
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Host "  ✓ Created .env from .env.example" -ForegroundColor Green
        } elseif (Test-Path ".env.production.example") {
            Copy-Item ".env.production.example" ".env"
            Write-Host "  ✓ Created .env from .env.production.example" -ForegroundColor Green
        } else {
            Write-Host "  ! No .env template found. Creating basic .env..." -ForegroundColor Yellow
            @"
# VidyaGuru Environment Configuration
ENVIRONMENT=development

# Database
POSTGRES_USER=vidyaguru
POSTGRES_PASSWORD=vidyaguru_dev
POSTGRES_DB=vidyaguru
DATABASE_URL=postgresql+asyncpg://vidyaguru:vidyaguru_dev@postgres:5432/vidyaguru

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=vidyaguru_redis

# Security
SECRET_KEY=dev_secret_key_change_in_production_$(Get-Random -Maximum 999999)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Gemini API
GEMINI_API_KEY=your_api_key_here

# CORS
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
"@ | Out-File -FilePath ".env" -Encoding UTF8
            Write-Host "  ✓ Created basic .env file" -ForegroundColor Green
        }
        
        Write-Host "`n  ⚠ IMPORTANT: Update .env with your GEMINI_API_KEY!" -ForegroundColor Yellow
        Write-Host "  Get your API key from: https://makersuite.google.com/app/apikey" -ForegroundColor Cyan
    } else {
        Write-Host "  ✓ .env file already exists" -ForegroundColor Green
    }
    
    # Generate SECRET_KEY if placeholder
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "dev_secret_key|change_in_production|<GENERATE") {
        $newSecret = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
        Write-Host "  ! Weak SECRET_KEY detected. Consider updating it." -ForegroundColor Yellow
    }
}

# Build containers
function Build-Containers {
    Write-Host "`n[3/5] Building containers..." -ForegroundColor Yellow
    
    if ($SkipBuild) {
        Write-Host "  • Skipping build (using --SkipBuild flag)" -ForegroundColor Cyan
        return
    }
    
    try {
        docker-compose build --parallel
        Write-Host "  ✓ Containers built successfully" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Build failed: $_" -ForegroundColor Red
        exit 1
    }
}

# Start services
function Start-Services {
    Write-Host "`n[4/5] Starting services..." -ForegroundColor Yellow
    
    $profile = ""
    if ($Production) {
        $profile = "--profile production"
        Write-Host "  • Starting in PRODUCTION mode" -ForegroundColor Magenta
    } elseif ($WithDevTools) {
        $profile = "--profile dev"
        Write-Host "  • Starting with development tools (pgAdmin, Redis Commander)" -ForegroundColor Cyan
    }
    
    try {
        $cmd = "docker-compose $profile up -d"
        Invoke-Expression $cmd
        Write-Host "  ✓ Services started" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to start services: $_" -ForegroundColor Red
        exit 1
    }
}

# Run migrations
function Invoke-Migrations {
    Write-Host "`n[5/5] Running database migrations..." -ForegroundColor Yellow
    
    # Wait for database to be ready
    Write-Host "  • Waiting for database..." -ForegroundColor Cyan
    $maxAttempts = 30
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        try {
            $result = docker-compose exec -T postgres pg_isready -U vidyaguru 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✓ Database is ready" -ForegroundColor Green
                break
            }
        } catch { }
        
        $attempt++
        Start-Sleep -Seconds 2
    }
    
    if ($attempt -eq $maxAttempts) {
        Write-Host "  ✗ Database not ready after ${maxAttempts} attempts" -ForegroundColor Red
        exit 1
    }
    
    # Run migrations
    try {
        docker-compose exec -T backend alembic upgrade head
        Write-Host "  ✓ Migrations completed" -ForegroundColor Green
    } catch {
        Write-Host "  ! Migration warning: $_" -ForegroundColor Yellow
    }
}

# Display status
function Show-Status {
    Write-Host "`n" -NoNewline
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "                    Setup Complete!                            " -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    
    Write-Host "`nServices:" -ForegroundColor Yellow
    docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    
    Write-Host "`n📚 Access Points:" -ForegroundColor Yellow
    Write-Host "  • Frontend:     http://localhost:3000" -ForegroundColor White
    Write-Host "  • Backend API:  http://localhost:8000" -ForegroundColor White
    Write-Host "  • API Docs:     http://localhost:8000/docs" -ForegroundColor White
    
    if ($WithDevTools) {
        Write-Host "  • PgAdmin:      http://localhost:5050" -ForegroundColor Cyan
        Write-Host "  • Redis Commander: http://localhost:8081" -ForegroundColor Cyan
    }
    
    if ($Production) {
        Write-Host "  • NGINX Proxy:  https://localhost (requires SSL setup)" -ForegroundColor Magenta
    }
    
    Write-Host "`n📋 Quick Commands:" -ForegroundColor Yellow
    Write-Host "  • View logs:      docker-compose logs -f" -ForegroundColor White
    Write-Host "  • Stop services:  docker-compose down" -ForegroundColor White
    Write-Host "  • Restart:        docker-compose restart" -ForegroundColor White
    
    Write-Host "`n⚠️  Don't forget to:" -ForegroundColor Yellow
    Write-Host "  1. Update GEMINI_API_KEY in .env" -ForegroundColor White
    Write-Host "  2. Change default passwords for production" -ForegroundColor White
    
    Write-Host "`n" -NoNewline
}

# Main execution
Test-Prerequisites
Set-Environment
Build-Containers
Start-Services
Invoke-Migrations
Show-Status

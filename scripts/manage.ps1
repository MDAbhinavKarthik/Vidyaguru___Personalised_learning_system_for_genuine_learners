# VidyaGuru AI - Management Commands
# Usage: .\scripts\manage.ps1 <command>

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "restart", "logs", "status", "migrate", "backup", "shell", "test", "clean", "help")]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$Service = "",
    
    [switch]$Dev,
    [switch]$Production,
    [switch]$Follow,
    [int]$Tail = 100
)

$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host "
VidyaGuru AI - Management Commands
===================================

Usage: .\scripts\manage.ps1 <command> [service] [options]

Commands:
  start       Start all services (or specific service)
  stop        Stop all services
  restart     Restart services
  logs        View service logs
  status      Show service status
  migrate     Run database migrations
  backup      Backup database
  shell       Open shell in container
  test        Run tests
  clean       Clean up containers and volumes
  help        Show this help

Options:
  -Service    Target specific service (backend, frontend, postgres, redis)
  -Dev        Include development tools (pgAdmin, Redis Commander)
  -Production Run in production mode with nginx
  -Follow     Follow log output (for logs command)
  -Tail       Number of log lines to show (default: 100)

Examples:
  .\scripts\manage.ps1 start                 # Start all services
  .\scripts\manage.ps1 start -Dev            # Start with dev tools
  .\scripts\manage.ps1 logs backend -Follow  # Follow backend logs
  .\scripts\manage.ps1 shell backend         # Open backend shell
  .\scripts\manage.ps1 backup                # Backup database
  .\scripts\manage.ps1 test                  # Run tests
"
}

function Start-VidyaGuru {
    Write-Host "Starting VidyaGuru services..." -ForegroundColor Green
    
    $profile = ""
    if ($Production) { $profile = "--profile production" }
    elseif ($Dev) { $profile = "--profile dev" }
    
    if ($Service) {
        Invoke-Expression "docker-compose $profile up -d $Service"
    } else {
        Invoke-Expression "docker-compose $profile up -d"
    }
    
    Write-Host "Services started!" -ForegroundColor Green
    docker-compose ps
}

function Stop-VidyaGuru {
    Write-Host "Stopping VidyaGuru services..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "Services stopped." -ForegroundColor Green
}

function Restart-VidyaGuru {
    Write-Host "Restarting VidyaGuru services..." -ForegroundColor Yellow
    
    if ($Service) {
        docker-compose restart $Service
    } else {
        docker-compose restart
    }
    
    Write-Host "Services restarted." -ForegroundColor Green
}

function Show-Logs {
    $tailArg = "--tail=$Tail"
    $followArg = if ($Follow) { "-f" } else { "" }
    
    if ($Service) {
        Invoke-Expression "docker-compose logs $tailArg $followArg $Service"
    } else {
        Invoke-Expression "docker-compose logs $tailArg $followArg"
    }
}

function Show-Status {
    Write-Host "`nService Status:" -ForegroundColor Cyan
    docker-compose ps
    
    Write-Host "`nResource Usage:" -ForegroundColor Cyan
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

function Invoke-Migration {
    Write-Host "Running database migrations..." -ForegroundColor Yellow
    docker-compose exec backend alembic upgrade head
    Write-Host "Migrations completed!" -ForegroundColor Green
}

function Backup-Database {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "backup_$timestamp.sql"
    $backupDir = "backups"
    
    # Create backup directory
    if (-not (Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir | Out-Null
    }
    
    Write-Host "Creating database backup..." -ForegroundColor Yellow
    docker-compose exec -T postgres pg_dump -U vidyaguru vidyaguru > "$backupDir\$backupFile"
    
    if ($?) {
        Write-Host "Backup saved to: $backupDir\$backupFile" -ForegroundColor Green
        
        # Show backup size
        $size = (Get-Item "$backupDir\$backupFile").Length / 1KB
        Write-Host "Backup size: $([math]::Round($size, 2)) KB" -ForegroundColor Cyan
    } else {
        Write-Host "Backup failed!" -ForegroundColor Red
    }
}

function Open-Shell {
    $targetService = if ($Service) { $Service } else { "backend" }
    
    Write-Host "Opening shell in $targetService..." -ForegroundColor Cyan
    
    switch ($targetService) {
        "backend" { docker-compose exec backend bash }
        "frontend" { docker-compose exec frontend sh }
        "postgres" { docker-compose exec postgres psql -U vidyaguru }
        "redis" { docker-compose exec redis redis-cli }
        default { docker-compose exec $targetService sh }
    }
}

function Invoke-Tests {
    Write-Host "Running tests..." -ForegroundColor Yellow
    
    if ($Service -eq "frontend" -or -not $Service) {
        Write-Host "`n=== Frontend Tests ===" -ForegroundColor Cyan
        docker-compose exec frontend npm test 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Frontend tests skipped or failed" -ForegroundColor Yellow
        }
    }
    
    if ($Service -eq "backend" -or -not $Service) {
        Write-Host "`n=== Backend Tests ===" -ForegroundColor Cyan
        docker-compose exec backend pytest -v
    }
}

function Clean-VidyaGuru {
    Write-Host "This will remove all containers, volumes, and images for VidyaGuru." -ForegroundColor Red
    $confirm = Read-Host "Are you sure? (y/N)"
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Write-Host "Stopping services..." -ForegroundColor Yellow
        docker-compose down -v --rmi local
        
        Write-Host "Pruning unused resources..." -ForegroundColor Yellow
        docker system prune -f
        
        Write-Host "Cleanup complete!" -ForegroundColor Green
    } else {
        Write-Host "Cleanup cancelled." -ForegroundColor Yellow
    }
}

# Main execution
switch ($Command) {
    "start"   { Start-VidyaGuru }
    "stop"    { Stop-VidyaGuru }
    "restart" { Restart-VidyaGuru }
    "logs"    { Show-Logs }
    "status"  { Show-Status }
    "migrate" { Invoke-Migration }
    "backup"  { Backup-Database }
    "shell"   { Open-Shell }
    "test"    { Invoke-Tests }
    "clean"   { Clean-VidyaGuru }
    "help"    { Show-Help }
    default   { Show-Help }
}

#!/usr/bin/env pwsh
# VidyaGuru Deployment Script for Vercel & Render
# This script helps prepare your project for deployment

Write-Host "🚀 VidyaGuru Deployment Setup Script" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
$checks = @{
    "Git" = { git --version | Out-Null }
    "Node.js" = { node --version | Out-Null }
    "npm" = { npm --version | Out-Null }
    "Python" = { python --version | Out-Null }
}

$allChecked = $true
foreach ($check in $checks.GetEnumerator()) {
    try {
        & $check.Value
        Write-Host "✅ $($check.Key) found" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ $($check.Key) not found - please install it" -ForegroundColor Red
        $allChecked = $false
    }
}

if (-not $allChecked) {
    Write-Host ""
    Write-Host "⚠️  Please install missing dependencies before continuing" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ All prerequisites met!" -ForegroundColor Green
Write-Host ""

# Generate secrets
Write-Host "🔐 Generating secure secrets..." -ForegroundColor Yellow
Write-Host ""

# Secret Key (32 bytes = 256 bits)
$secretKey = [Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
Write-Host "SECRET_KEY generated: $(($secretKey).Substring(0, 20))..." -ForegroundColor Green

# DB Password
$dbPassword = [Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(24))
Write-Host "DB_PASSWORD generated: $(($dbPassword).Substring(0, 20))..." -ForegroundColor Green

# Redis Password  
$redisPassword = [Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(24))
Write-Host "REDIS_PASSWORD generated: $(($redisPassword).Substring(0, 20))..." -ForegroundColor Green

Write-Host ""
Write-Host "📝 Secrets to save (copy to Render environment variables):" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "SECRET_KEY=$secretKey" -ForegroundColor White
Write-Host "DB_PASSWORD=$dbPassword" -ForegroundColor White
Write-Host "REDIS_PASSWORD=$redisPassword" -ForegroundColor White
Write-Host ""

# Save to file
$secretsFile = "DEPLOYMENT_SECRETS.txt"
@"
🔐 VidyaGuru Deployment Secrets
Generated: $(Get-Date)

⚠️  KEEP THIS FILE SECURE - DO NOT COMMIT TO GIT!
⚠️  Delete after adding to Render environment variables

SECRET_KEY=$secretKey
DB_PASSWORD=$dbPassword
REDIS_PASSWORD=$redisPassword

NEXT STEPS:
1. Copy these values to Render environment variables
2. Add Gemini API Key to GEMINI_API_KEY environment variable
3. Deploy backend first, get the URL
4. Add backend URL as NEXT_PUBLIC_API_URL to Vercel
5. Delete this file after deployment
"@ | Out-File $secretsFile -Encoding UTF8

Write-Host "💾 Secrets saved to: $secretsFile" -ForegroundColor Green
Write-Host "⚠️  Keep this file secure and delete after setup" -ForegroundColor Yellow
Write-Host ""

# Check frontend build
Write-Host "🔨 Building frontend..." -ForegroundColor Yellow
Push-Location frontend
npm run build
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend build successful" -ForegroundColor Green
}
else {
    Write-Host "❌ Frontend build failed" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

Write-Host ""
Write-Host "📦 Frontend build output ready for Vercel" -ForegroundColor Green
Write-Host ""

# Git status
Write-Host "📚 Git status:" -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "✅ Deployment preparation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Push code to GitHub: git push origin main" -ForegroundColor White
Write-Host "2. Create Render Blueprint: https://render.com/dashboard" -ForegroundColor White
Write-Host "3. Add secrets from DEPLOYMENT_SECRETS.txt to Render" -ForegroundColor White
Write-Host "4. Deploy backend and get the URL" -ForegroundColor White
Write-Host "5. Create Vercel project: https://vercel.com/new" -ForegroundColor White
Write-Host "6. Add NEXT_PUBLIC_API_URL environment variable to Vercel" -ForegroundColor White
Write-Host ""
Write-Host "📖 Full guide: VERCEL_DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan

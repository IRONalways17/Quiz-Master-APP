# Quiz Master V2 - PowerShell Heroku Deployment Script
# Run this script in PowerShell from the project root directory

Write-Host "Quiz Master V2 - PowerShell Heroku Deployment" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Function to display colored output
function Write-Status {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Error {
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Warning {
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

# Check if we're in the right directory
if (-not (Test-Path "README.md") -or -not (Test-Path "frontend") -or -not (Test-Path "backend")) {
    Write-Error "Please run this script from the project root directory (Quiz2)"
    exit 1
}

# Check if Heroku CLI is installed
try {
    $herokuVersion = heroku --version
    Write-Success "Heroku CLI found: $($herokuVersion.Split([Environment]::NewLine)[0])"
} catch {
    Write-Error "Heroku CLI is not installed. Please install it first."
    Write-Status "Download from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
}

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Success "Git found: $gitVersion"
} catch {
    Write-Error "Git is not installed. Please install Git first."
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Success "Node.js found: $nodeVersion"
} catch {
    Write-Error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
}

Write-Status "Building frontend for production..."
Set-Location frontend
try {
    npm run build
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Frontend build completed successfully"
    } else {
        Write-Error "Frontend build failed"
        exit 1
    }
} catch {
    Write-Error "Frontend build failed"
    exit 1
}

Set-Location ..

# Copy built frontend to backend static directory
Write-Status "Copying frontend build to backend..."
if (Test-Path "backend\static") {
    Remove-Item -Recurse -Force "backend\static"
}
Copy-Item -Recurse "frontend\dist" "backend\static"
Write-Success "Frontend copied to backend static directory"

# Initialize git if not already done
if (-not (Test-Path ".git")) {
    Write-Status "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit"
}

# Set git user config for this repository
Write-Status "Setting git user configuration..."
git config user.email "developer@quizmaster.com"
git config user.name "Quiz Master Developer"

# Add all files and commit
Write-Status "Adding files and creating commit..."
git add .
git commit -m "Deploy to Heroku - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

Write-Success "Project prepared for Heroku deployment!"
Write-Warning "Next steps:"
Write-Host ""
Write-Host "1. Login to Heroku:" -ForegroundColor Yellow
Write-Host "   heroku login" -ForegroundColor White
Write-Host ""
Write-Host "2. Add Heroku remote:" -ForegroundColor Yellow
Write-Host "   heroku git:remote -a quiz-master-app" -ForegroundColor White
Write-Host ""
Write-Host "3. Add required addons:" -ForegroundColor Yellow
Write-Host "   heroku addons:create heroku-postgresql:essential-0" -ForegroundColor White
Write-Host "   heroku addons:create heroku-redis:mini" -ForegroundColor White
Write-Host ""
Write-Host "4. Set environment variables:" -ForegroundColor Yellow
Write-Host "   heroku config:set FLASK_ENV=production" -ForegroundColor White
Write-Host "   heroku config:set SECRET_KEY=your-secret-key-here" -ForegroundColor White
Write-Host "   heroku config:set JWT_SECRET_KEY=your-jwt-secret-here" -ForegroundColor White
Write-Host "   heroku config:set ADMIN_EMAIL=admin@quizmaster.com" -ForegroundColor White
Write-Host "   heroku config:set ADMIN_PASSWORD=YourSecurePassword123!" -ForegroundColor White
Write-Host ""
Write-Host "5. Deploy to Heroku:" -ForegroundColor Yellow
Write-Host "   git push heroku master" -ForegroundColor White
Write-Host ""
Write-Host "6. Open your app:" -ForegroundColor Yellow
Write-Host "   heroku open" -ForegroundColor White

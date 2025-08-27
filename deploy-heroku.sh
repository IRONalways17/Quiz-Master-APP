#!/bin/bash

echo "Quiz Master V2 - Heroku Deployment Script"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    print_error "Heroku CLI is not installed. Please install it first."
    print_status "Visit: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_status "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit"
fi

# Check if Heroku remote exists
if ! git remote | grep -q heroku; then
    print_warning "Heroku remote not found. Please run:"
    print_status "heroku git:remote -a quiz-master-app"
    exit 1
fi

# Build frontend
print_status "Building frontend for production..."
cd frontend
npm run build
if [ $? -ne 0 ]; then
    print_error "Frontend build failed"
    exit 1
fi
cd ..

# Copy built frontend to backend static directory
print_status "Copying frontend build to backend..."
rm -rf backend/static
cp -r frontend/dist backend/static

# Create app.json for Heroku
print_status "Creating Heroku app configuration..."
cat > app.json << EOF
{
  "name": "Quiz Master V2",
  "description": "A comprehensive quiz management system",
  "repository": "https://github.com/yourusername/quiz-master-v2",
  "logo": "https://raw.githubusercontent.com/23f2003700/B/refs/heads/main/topim.png",
  "keywords": ["flask", "vue", "quiz", "education"],
  "env": {
    "SECRET_KEY": {
      "description": "Secret key for Flask sessions",
      "generator": "secret"
    },
    "JWT_SECRET_KEY": {
      "description": "Secret key for JWT tokens",
      "generator": "secret"
    },
    "FLASK_ENV": {
      "description": "Flask environment",
      "value": "production"
    },
    "ADMIN_EMAIL": {
      "description": "Admin email address",
      "value": "admin@quizmaster.com"
    },
    "ADMIN_PASSWORD": {
      "description": "Admin password",
      "value": "admin123"
    }
  },
  "addons": [
    "heroku-postgresql:essential-0",
    "heroku-redis:mini"
  ],
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}
EOF

# Set environment variables
print_status "Setting up environment variables..."
print_warning "Make sure to set these environment variables in Heroku:"
echo "- SECRET_KEY (will be auto-generated)"
echo "- JWT_SECRET_KEY (will be auto-generated)"
echo "- FLASK_ENV=production"
echo "- ADMIN_EMAIL=admin@quizmaster.com"
echo "- ADMIN_PASSWORD=your_secure_password"

# Deploy to Heroku
print_status "Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku - $(date)"
git push heroku main

if [ $? -eq 0 ]; then
    print_success "Deployment completed successfully!"
    print_status "Your app should be available at: https://quiz-master-app.herokuapp.com"
    print_status "Run 'heroku logs --tail' to view logs"
else
    print_error "Deployment failed. Check the logs with 'heroku logs --tail'"
fi

@echo off
REM ============================================
REM ASIE Dashboard - Automated GitHub Push
REM ============================================

echo.
echo ========================================
echo  ASIE Dashboard - GitHub Setup
echo ========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo [ERROR] Git repository not found!
    echo Please run: git init
    exit /b 1
)

echo [1/4] Checking git status...
git status

echo.
echo [2/4] Please create a new repository on GitHub:
echo        1. Go to: https://github.com/new
echo        2. Repository name: asie-dashboard
echo        3. Keep it Public or Private
echo        4. DO NOT initialize with README
echo        5. Click "Create repository"
echo.
echo [3/4] Enter your GitHub username:
set /p GITHUB_USER=Username: 

echo.
echo [4/4] Pushing to GitHub...
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/%GITHUB_USER%/asie-dashboard.git
git push -u origin main

echo.
echo ========================================
echo  SUCCESS! Code pushed to GitHub
echo ========================================
echo.
echo Your repository: https://github.com/%GITHUB_USER%/asie-dashboard
echo.
echo NEXT STEPS:
echo 1. Deploy backend to Render: https://render.com
echo 2. Deploy frontend to Vercel: https://vercel.com
echo 3. See DEPLOYMENT_GUIDE.md for details
echo.
pause

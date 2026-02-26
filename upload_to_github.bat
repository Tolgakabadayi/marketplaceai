@echo off
setlocal

echo ========================================
echo MarketplaceAI.shop - GitHub Upload Helper
echo ========================================

:: Check for .git folder
if not exist ".git" (
    echo Initializing Git repository...
    git init
)

:: Add files
echo Adding files to staging...
git add .

:: Commit
set /p commit_msg="Enter commit message (default: 'Initial commit from automated script'): "
if "%commit_msg%"=="" set commit_msg=Initial commit from automated script
git commit -m "%commit_msg%"

:: Branch
echo Setting branch to main...
git branch -M main

:: Remote
echo.
echo Please go to your browser, create a NEW repository on GitHub,
echo and copy the 'HTTPS' or 'SSH' remote URL.
echo (e.g., https://github.com/your-username/your-repo.git)
echo.
set /p remote_url="Paste your GitHub repository URL here: "

if "%remote_url%"=="" (
    echo [ERROR] Repository URL is required. Exiting.
    pause
    exit /b
)

:: Check if remote already exists
git remote remove origin >nul 2>&1
git remote add origin %remote_url%

:: Push
echo.
echo Pushing to GitHub...
echo (You may be asked to log in via a browser popup)
echo.
git push -u origin main

echo.
echo ========================================
echo DONE! Check your GitHub repository.
echo ========================================
pause

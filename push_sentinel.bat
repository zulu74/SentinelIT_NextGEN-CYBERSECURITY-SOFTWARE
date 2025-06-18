
@echo off
setlocal

REM Check if repo URL is passed
if "%~1"=="" (
  echo Usage: push_sentinel.bat https://github.com/your-username/your-repo.git
  exit /b 1
)

set REPO_URL=%~1

echo 🔄 Initializing Git repository...
git init

echo 📂 Adding updated and new SentinelIT modules...
git add ultimate_main.py vaultwatch.py vaultwatch_install.py vaultwatch_reboot.py resurgwatch.py traveltrap_email.py aihelpdesk.py *.txt *.md *.json *.png *.jpg *.spec 2>nul

echo ✅ Committing SentinelIT module updates...
git commit -m "Updated SentinelIT: vault security modules (vaultwatch, install, reboot), AI helpdesk (no OTP), phishing email patch, resurgwatch fix."

echo 🔗 Linking to GitHub remote...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%

echo 🚀 Pushing to main branch...
git branch -M main
git push -u origin main

echo ✅ Push complete. All major SentinelIT updates deployed to GitHub.
pause

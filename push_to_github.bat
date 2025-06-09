
@echo off
cd /d "C:\Users\zxola\Downloads\SentinelIT_Build"
git init
git remote remove origin 2>nul
git remote add origin https://github.com/zulu74/SentinelIT_NextGEN-CYBERSECURITY-SOFTWARE.git
git pull origin main
git add .
git commit -m "Updated SentinelIT modules and fixed all imports"
git push origin main
pause

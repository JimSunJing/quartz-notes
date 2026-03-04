@echo off
setlocal

cd /d "%~dp0"

where git >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Git is not installed or not in PATH.
  pause
  exit /b 1
)

git rev-parse --is-inside-work-tree >nul 2>nul
if errorlevel 1 (
  echo [ERROR] This folder is not a Git repository.
  pause
  exit /b 1
)

for /f "delims=" %%i in ('git rev-parse --abbrev-ref HEAD 2^>nul') do set "CURRENT_BRANCH=%%i"
if not defined CURRENT_BRANCH (
  echo [ERROR] Unable to detect current branch.
  pause
  exit /b 1
)

for /f "delims=" %%i in ('git remote get-url origin 2^>nul') do set "ORIGIN_URL=%%i"
if not defined ORIGIN_URL (
  echo [ERROR] Remote "origin" is not configured.
  echo Run: git remote add origin https://github.com/yourname/yourrepo.git
  pause
  exit /b 1
)

if "%~1"=="" (
  set "COMMIT_MSG=chore: auto update %date% %time%"
) else (
  set "COMMIT_MSG=%*"
)

echo.
echo [INFO] Branch: %CURRENT_BRANCH%
echo [INFO] Remote: %ORIGIN_URL%
echo [INFO] Commit message: %COMMIT_MSG%
echo.

git add -A
if errorlevel 1 (
  echo [ERROR] git add failed.
  pause
  exit /b 1
)

git diff --cached --quiet
if errorlevel 1 (
  git commit -m "%COMMIT_MSG%"
  if errorlevel 1 (
    echo [ERROR] git commit failed.
    pause
    exit /b 1
  )
) else (
  echo [INFO] No staged changes. Skip commit.
)

git push -u origin %CURRENT_BRANCH%
if errorlevel 1 (
  echo [ERROR] git push failed.
  echo Tips:
  echo 1^) Check GitHub login/token.
  echo 2^) If first push, verify repo permissions.
  pause
  exit /b 1
)

echo [DONE] Pushed to GitHub successfully.
pause
exit /b 0

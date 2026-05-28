@echo off
cd /d "%~dp0"

echo === RUN C2 AUDIT ===

echo [1] Git Status
git status

echo [2] Dangerous Files
git ls-files | findstr /i "\.idea \.pytest_cache mingw64 git-bash.exe git-cmd.exe \.exe \.dll"

echo [3] VALIDATOR
python scripts\c2_validate.py --strict

echo [4] SCORE CHECK
python scripts\c2_score_check.py

echo [5] SECRET SCAN
python scripts\c2_secret_scan.py

echo [6] TESTS
python -m pytest tests\ -v

echo === END ===

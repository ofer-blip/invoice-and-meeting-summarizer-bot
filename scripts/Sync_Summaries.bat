@echo off
title D-Dialog Meeting Summarizer Sync
echo ===================================================
echo     D-Dialog - Syncing Meeting Summaries (MD)
echo ===================================================
echo.
cd /d "%~dp0"
python sync_summaries.py
echo.
pause

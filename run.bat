@echo off
title AbilityV2 - Made by Baahwei
cd /d "%~dp0"
echo.
echo [*] Installing requirements...
python -m pip install -r requirements.txt -q
echo [*] Starting AbilityV2...
echo.
python abilityv2.py
pause
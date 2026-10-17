@echo off
echo ======================================================================
echo Launching Android Architecture ^& Code Deep-Dive Web Application...
echo ======================================================================
echo.
echo Opening index.html in your default web browser...
start "" "%~dp0index.html"
echo.
echo If you would like to run a local HTTP server instead, run:
echo   python -m http.server 8080
echo and navigate to http://localhost:8080
echo.
pause


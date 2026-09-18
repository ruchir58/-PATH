@echo off
echo ===================================================
echo Starting प्रगति-PATH Student Risk Warning System...
echo ===================================================

echo.
echo Starting FastAPI Backend...
start "Backend Server" cmd /c "cd backend && call venv\Scripts\activate && uvicorn app.main:app --reload --port 8005"

echo Starting Next.js Frontend...
start "Frontend Server" cmd /c "npm run dev"

echo.
echo Waiting a few seconds for Next.js to boot up...
timeout /t 5 /nobreak > NUL

echo Opening dashboard in your default browser...
start http://localhost:3005

echo.
echo Servers are running in the separate windows!
echo - Backend API Docs: http://localhost:8005/docs
echo - Frontend Application: http://localhost:3005
echo.
echo You can close this window now.
pause

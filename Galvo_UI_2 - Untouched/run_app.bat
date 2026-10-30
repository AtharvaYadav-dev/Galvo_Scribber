@echo off
echo ===================================================
echo   GALVO LASER STUDIO PRO // NATIVE DESKTOP MODE
echo ===================================================
echo.
if not exist "frontend\dist\index.html" (
    echo Production build not found. Building frontend now...
    cd frontend && npm run build && cd ..
)
echo Launching native desktop window...
python app.py --prod

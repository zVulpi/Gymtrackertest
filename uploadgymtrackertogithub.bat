@echo off
set /p comment="Was hast du geandert? (Commit Message): "

echo.
echo Fuege Dateien hinzu...
git add .

echo.
echo Erstelle Speicherpunkt...
git commit -m "%comment%"

echo.
echo Lade auf GitHub hoch...
git push

echo.
echo --- FERTIG! Render.com baut jetzt deine App neu. ---
pause
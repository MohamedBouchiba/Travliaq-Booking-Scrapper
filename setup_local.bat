@echo off
echo Installation locale de Travliaq-Booking-Scrapper
echo ================================================

REM Créer un environnement virtuel
python -m venv venv

REM Activer l'environnement
call venv\Scripts\activate.bat

REM Installer les dépendances
pip install -r requirements.txt

REM Installer les navigateurs Playwright
playwright install chromium

REM Copier le fichier .env
if not exist .env (
    copy .env.example .env
    echo Fichier .env cree. Configurez-le selon vos besoins.
)

echo.
echo Installation terminee!
echo.
echo Pour lancer l'application:
echo   1. Activez l'environnement: venv\Scripts\activate.bat
echo   2. Lancez l'API: uvicorn src.api.main:app --reload --port 8000
echo.
pause

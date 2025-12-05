@echo off
cls
echo ========================================================
echo        CONSTRUYENDO TU APP: BINANCE HUNTER
echo ========================================================
echo.
echo [1/3] Instalando el compilador (PyInstaller)...
pip install pyinstaller

echo.
echo [2/3] Empaquetando el codigo, el cerebro y el dashboard...
echo       Esto puede tardar unos minutos. Paciencia, mami.
echo.

rem --onefile: Crea un solo archivo .exe
rem --name: El nombre de tu app
rem --clean: Limpia cache anterior
rem --hidden-import: Asegura que las librerias clave se metan a la maleta

pyinstaller --noconfirm --onefile --console --name "BinanceHunter" --clean --hidden-import="rich" --hidden-import="telethon" --hidden-import="sqlite3"  main.py

echo.
echo [3/3] Limpiando basura de la construccion...
rd /s /q build
del BinanceHunter.spec

echo.
echo ========================================================
echo        LISTO! TU APP ESTA EN LA CARPETA 'dist'
echo ========================================================
echo.
pause

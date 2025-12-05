@echo off
:loop
cls
echo ====================================================
echo       Iniciando el Bot de Binance (Modo Inmortal)
echo ====================================================
python main.py
echo.
echo El bot se ha detenido o reiniciado.
echo Volviendo a iniciar en 3 segundos...
timeout /t 3
goto loop
sii
#!/bin/bash
while true
do
    clear
    echo "===================================================="
    echo "       Iniciando el Bot de Binance (Modo Linux)     "
    echo "===================================================="
    python3 main.py
    echo
    echo "El bot se ha detenido o reiniciado."
    echo "Volviendo a iniciar en 3 segundos..."
    sleep 3
done

@echo off
title Aplicacion de Ocupabilidad
echo ========================================
echo   APLICACION WEB DE OCUPABILIDAD
echo ========================================
echo.
echo   Iniciando servidor...
echo.

REM Iniciar servidor en segundo plano
start /b python app.py

REM Esperar 3 segundos para que el servidor inicie
timeout /t 3 /nobreak >nul

REM Abrir navegador
start http://localhost:5000

echo.
echo   Servidor iniciado. Navegador abierto.
echo   Presiona Ctrl+C para detener
echo ========================================
echo.

REM Mantener ventana abierta
pause

@echo off
cd /d "%~dp0"
title Sistema de Vision Artificial - Local
color 0A



python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH del sistema.
    echo Por favor, instale Python e intentelo nuevamente.
    pause
    exit /b 1
)


echo [1/3] Verificando compilacion de Frontend...
if not exist "frontend\dist\index.html" (
    echo [ERROR] Frontend no esta construido. Construyendo ahora...
    cd frontend
    call npm install
    call npm run build
    cd ..
) else (
    echo [OK] Frontend ya esta construido.
)


echo [2/3] Configurando Motor de Inteligencia Artificial...
cd ai
set RECONSTRUIR_AI_VENV=0

if not exist venv\Scripts\activate.bat goto crear_ai_venv


venv\Scripts\python.exe -c "import sys" >nul 2>&1
if errorlevel 1 goto corrupto_ai_venv
goto saltar_crear_ai

:corrupto_ai_venv
echo [ADVERTENCIA] El entorno virtual de IA esta corrupto o tiene rutas invalidas. Reconstruyendo...
rd /s /q venv

:crear_ai_venv
set RECONSTRUIR_AI_VENV=1

:saltar_crear_ai
if "%RECONSTRUIR_AI_VENV%"=="1" (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual en 'ai'.
        cd ..
        pause
        exit /b 1
    )
    echo [INFO] Instalando dependencias en motor de IA, esto puede tomar unos minutos...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] No se pudieron instalar las dependencias del motor de IA.
        cd ..
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual de IA configurado correctamente.
) else (
    echo [OK] Entorno virtual de IA validado y listo.
)
cd ..


echo [INFO] Iniciando Motor de Inteligencia Artificial (Headless)...
start "Motor IA" cmd /c "cd ai && call venv\Scripts\activate.bat && python src\app.py || pause"


echo [3/3] Configurando Backend...
cd backend
set RECONSTRUIR_BACKEND_VENV=0

if not exist venv\Scripts\activate.bat goto crear_backend_venv


venv\Scripts\python.exe -c "import sys" >nul 2>&1
if errorlevel 1 goto corrupto_backend_venv
goto saltar_crear_backend

:corrupto_backend_venv
echo [ADVERTENCIA] El entorno virtual del Backend esta corrupto o tiene rutas invalidas. Reconstruyendo...
rd /s /q venv

:crear_backend_venv
set RECONSTRUIR_BACKEND_VENV=1

:saltar_crear_backend
if "%RECONSTRUIR_BACKEND_VENV%"=="1" (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual en 'backend'.
        cd ..
        pause
        exit /b 1
    )
    echo [INFO] Instalando dependencias en el Backend...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] No se pudieron instalar las dependencias del Backend.
        cd ..
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual del Backend configurado correctamente.
) else (
    echo [OK] Entorno virtual del Backend validado y listo.
)

echo.
echo ========================================================
echo TODO EL SISTEMA INICIADO.
echo Abra su navegador en: http://localhost:8000
echo ========================================================
call venv\Scripts\activate.bat
python main.py

pause

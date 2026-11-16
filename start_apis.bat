@echo off
rem set "PY=%~dp0.api_env\Scripts\python.exe"
set "PY=%~dp0venv\Scripts\python.exe"

rem lanzar servicio de usuarios
start cmd /k "cd /d %~dp0Usuarios && "%PY%" run.py"
echo servicio de usuarios levantado

rem lanzar servicio de clientes
start cmd /k "cd /d %~dp0Clients && "%PY%" run.py"
echo servicio de clientes levantado

rem lanzar servicio de servicios
start cmd /k "cd /d %~dp0Servicios && "%PY%" run.py"
echo servicio de servicios levantado

rem lanzar servicio de maquinas
start cmd /k "cd /d %~dp0Maquinas && "%PY%" run.py"
echo servicio de maquinas levantado

rem lanzar servicio de turnos
start cmd /k "cd /d %~dp0Turnos && "%PY%" run.py"
echo servicio de turnos levantado

rem lanzar servicio de tickets
start cmd /k "cd /d %~dp0Ticket && "%PY%" run.py"
echo servicio de tickets levantado

rem lanzar api gateway
start cmd /k "cd /d %~dp0 && "%PY%" gateway.py"
echo api gateway levantado

pause   
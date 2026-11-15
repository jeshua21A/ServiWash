#!/bin/bash

# Iniciando cada Microservicio en segundo plano (&) y guardar sus PIDs
python3 Usuarios/run.py &
PID1=$!

python3 Clients/run.py &
PID2=$!

python3 Maquinas/run.py &
PID3=$!

python3 Servicios/run.py &
PID4=$!

python3 Turnos/run.py &
PID5=$!

python3 Ticket/run.py &
PID6=$!

# Iniciar el API Gateway al final
python3 gateway.py &
PID7=$!

echo ""
echo "-----------------------------------------"
echo "Todos los servicios están corriendo..."
echo "Precione [Ctrl + C] para apagarlos todos."
echo "-----------------------------------------"
echo ""

# Trampa para interceptar: Ctrl+C, mostrar mensajes y finalizar cada servicio ordenadamente
trap '
    echo ""
    echo ""
    echo "---------------------------------------------------------------"
    echo "Señal recibida. Apagando los 7 servicios..."
    kill $PID1 $PID2 $PID3 $PID4 $PID5 $PID6 $PID7 2>/dev/null
    echo "¡Todos los servicios (APIs y Gateway) se han cerrado con éxito!"
    echo "---------------------------------------------------------------"
    echo ""
    exit 0
' INT

# Esperando Ctrl+C para matar todos los procesos guardados
wait
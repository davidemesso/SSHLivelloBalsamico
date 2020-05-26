#!/bin/bash

pkill -f "python3.*"

python3 /home/messori/TornadoServer/Messori-Tornado-Server.py &> /dev/null &
python3 /home/messori/backendDataHandler.py &> /dev/null &

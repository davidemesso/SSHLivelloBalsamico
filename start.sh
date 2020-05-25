#!/bin/bash

cd TornadoServer/
python3 Messori-Tornado-Server.py &> /dev/null &
cd ..
python3 backendDataHandler.py &> /dev/null &

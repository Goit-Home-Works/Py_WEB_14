#!/bin/bash

echo Sleep 2....
sleep 2

cd ./src
alembic upgrade head
# uvicorn main:app --host 0.0.0.0 --port 9000
python ./main.py



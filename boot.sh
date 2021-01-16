#!/bin/bash
while true; do
    flask db init
    flask db migrate
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Init command failed, retrying in 5 secs...
    sleep 5
done
flask run

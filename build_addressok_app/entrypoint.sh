#!/bin/bash

if [ $@ == "update-db" ]; then
    cd /app
    python3 /app/wait_for_mysql.py
    if [ $? == 0 ]; then
        python3 check_update.py
    fi
else
    cd /app
    python3 /app/wait_for_mysql.py
    if [ $? == 0 ]; then
        echo "MySQL is available."
        # python3 /app/first_run.py
        # python3 app.py
        uwsgi --ini /conf/uwsgi.ini &
        service nginx restart
        exec "$@"
    else
        echo "MySQL is not available."
    fi
fi

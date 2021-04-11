#!/bin/sh

CMD="$1"
echo "command is: " $CMD
if [ "$CMD" = "uwsgi" ]; then
   uwsgi -H /venv --uid 1000 --socket 0.0.0.0:5000 --protocol=http -w baysiebins.wsgi:app
   exit
fi

exec "$@"


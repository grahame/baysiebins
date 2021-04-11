#!/bin/sh

CMD="$1"
echo "command is: " $CMD
if [ "$CMD" = "uwsgi" ]; then
   uwsgi --socket 0.0.0.0:5000 --protocol=http -w baysiebins.uwsgi:app
   exit
fi

exec "$@"


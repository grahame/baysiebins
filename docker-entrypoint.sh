#!/bin/sh

CMD="$1"
echo "command is: " $CMD
if [ "$CMD" = "gunicorn" ]; then
   gunicorn -w 3 --bind=0.0.0.0:5000 baysiebins.wsgi:app
   exit
fi

exec "$@"


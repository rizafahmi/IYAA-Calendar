uwsgi --http :6542 --wsgi-file calendar.wsgi --master --daemonize ./uwsig_calendar.log --pidfile ./pid_5000.pid --workers 3

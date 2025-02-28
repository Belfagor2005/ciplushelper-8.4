#!/bin/sh

VERSION=1

[ -x /usr/bin/ciplushelper ] || exit 0

case "$1" in
	start)
		if [ -n "`pidof /usr/bin/ciplushelper`" ] ; then
			echo "ciplushelper is already running!"
		else
			echo -n "Running ciplushelper..."
			/usr/bin/ciplushelper &
			sleep 2
			if [ -n "`pidof /usr/bin/ciplushelper`" ] ; then
				echo "done."
			else
				echo "ciplushelper failed start!"
			fi 
		fi
	;;
	stop)
		killall ciplushelper 2>/dev/null
		echo "done."
	;;
	restart)
		$0 stop
		sleep 3
		$0 start
	;;
	enable_autostart)
		update-rc.d ciplushelper defaults 50
	;;
	disable_autostart)
		update-rc.d -f ciplushelper remove
	;;
	*)
	echo " "
	echo "Options: $0 {start|stop|restart|enable_autostart|disable_autostart}"
	echo " "
	exit 1
esac

exit 0

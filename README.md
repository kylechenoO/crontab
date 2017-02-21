##Crontab Service in Python README
Dev Logs:
20170221v1:
	To optimize some funcs and test on Linux/MacOS. Stilling checking mem out. Add some comments;

20170220v1:
    To fix some lock bugs, and can use "python service.py [start|stop|restart|service]" to manager it. Change to use init() and destroy() funcs in crontab.py to initial some usefull values.
    NOW IT CAN BE USED.!

20170219v1:
    Just change into service mode, but found a new lock bug, must initial lock above all initial.

Usage:
    python bin/service.py [start|stop|restart|status]



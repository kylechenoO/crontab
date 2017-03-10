##Crontab Service in Python README
Dev Logs:

20170310v1:
        Fix log output bug and looks run better in Linux/Aix.

20170309v1:
	To Add AIX Support and Fix Some Bugs.

20170223v1:
	To Fix Python 2.6.6 Bugs.

20170222v1:
	To Fix Log Bugs;

20170221v1:
	To optimize some funcs and test on Linux/MacOS. Stilling checking mem out.

20170220v1:
    To fix some lock bugs, and can use "python service.py [start|stop|restart|service]" to manager it. Change to use init() and destroy() funcs in crontab.py to initial some usefull values.
    NOW IT CAN BE USED.!

20170219v1:
    Just change into service mode, but found a new lock bug, must initial lock above all initial.

Usage:
    python bin/service.py [start|stop|restart|status]



###############################################################################
## Service.Py
## the crontab service function
## Written By Kyle Chen
## Version 20170219v1
## Note:
##  add input args to manager crontab service
###############################################################################
#!/usr/bin/env python

##import pkgs
import kglobal;
import sys;
import os;
import re;

##init kglobal values
WORK_PTH=kglobal.get_wpth();
BIN_PTH=WORK_PTH + "/bin";
BIN_FP=BIN_PTH + "/crontab.py";
LOCK_PTH=WORK_PTH + "/lock";
LOCK_FP=LOCK_PTH + "/crontab.lock";
PROC_NAME=re.sub("\/", "\\/", BIN_FP);

##service_start
def service_start():

    cmd="python " + BIN_FP + " &> /dev/null &";
    os.system(cmd);
    sys.stdout.write("Starting Crontab Service            [started]\n");
    sys.stderr.flush();

    return(True);

##service_stop
def service_stop():

    global PROC_NAME;

    pidlst=kglobal.get_pidlst(PROC_NAME);
    if str(pidlst) != "":
        cmd="kill -9 " + pidlst;
        os.system(cmd);
        sys.stdout.write("Stopping Crontab Service            [stopped]\n");
        sys.stderr.flush();
        return(True);
    else:
        sys.stdout.write("Stopping Crontab Service            [stopped]\n");
        sys.stderr.write("Service Alreally Stopped\n");
        sys.stdout.flush();
        sys.stderr.flush();
        return(False);

##service_status
def service_status():

    global LOCK_FP;

    lock_stat=kglobal.lock_init(LOCK_FP);
    pidlst=kglobal.get_pidlst(PROC_NAME);

    if (str(pidlst) != "") and (int(lock_stat) == kglobal.LOCK_ST):
        sys.stdout.write("Service is Running\n");
        sys.stdout.flush();
        sys.exit(0);
    elif (str(pidlst) != "") and (int(lock_stat) == kglobal.LOCK_US):
        sys.stderr.write("Service Still Running But Lock is Free\n");
        sys.stderr.flush();
        sys.exit(1);
    elif (str(pidlst) == "") and (int(lock_stat) == kglobal.LOCK_ST):
        sys.stderr.write("Service is Not Running But Lock is Locked\n");
        sys.stderr.flush();
        sys.exit(3);
    else:
        sys.stderr.write("Service Alreally Stopped\n");
        sys.stderr.flush();
        sys.exit(4);

##usage function
def usage():
    sys.stdout.write(sys.argv[0] + " [start|stop|restart|status]\n");
    sys.stdout.flush();
    return(True);

##run function
def main():

    if sys.argv[1] == "start":
        service_start();
    elif sys.argv[1] == "stop":
        service_stop();
    elif sys.argv[1] == "restart":
        service_stop();
        service_start();
    elif sys.argv[1] == "status":
        service_status();
    else:
        usage();

    return(True);

##main function
if __name__ == "__main__":

    main();
    sys.exit(0);

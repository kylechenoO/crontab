###############################################################################
## Service.Py
## the crontab service function
## Written By Kyle Chen
## Version 201700310v1
## Note:
##  Fix log output bug and looks run better in Linux/Aix
###############################################################################
#!/usr/bin/env python

##import pkgs
import kglobal;
import crontab;
import sys;
import os;
import re;

##init kglobal values
WORK_PTH=kglobal.get_wpth();
BIN_PTH=WORK_PTH + "/bin";
BIN_FP=BIN_PTH + "/crontab.py";
LOCK_PTH=WORK_PTH + "/lock";
LOCK_FP=LOCK_PTH + "/crontab.lock";
LOG_PTH=WORK_PTH + "/log";
PROC_NAME=re.sub("\/", "\\/", BIN_FP);

##service_start
def service_start():

    ##global values
    global PROC_NAME;

    ##get pidlst
    pidlst=kglobal.get_pidlst(PROC_NAME);

    ##if is running print err output and return
    if str(pidlst) != "":

        ##error print
        sys.stderr.write("Starting Crontab Service            [started]\nAlreally Started\n");
        sys.stderr.flush();

        ##return False
        return(False);

    ##packed cmd value
    cmd="nohup python " + BIN_FP + " > /dev/null 2>&1 &";

    ##just run it
    os.system(cmd);

    ##stdout put
    sys.stdout.write("Starting Crontab Service            [started]\n");
    sys.stderr.flush();

    ##return True
    return(True);

##service_stop
def service_stop():

    ##global values
    global PROC_NAME;

    ##get pidlst
    pidlst=kglobal.get_pidlst(PROC_NAME);

    ##if is running destroy and stop service
    if str(pidlst) != "":

        ##run destroy() func
        crontab.destroy();

        ##packed cmd value
        cmd="kill -9 " + pidlst;

        ##run command
        os.system(cmd);

        ##system output
        sys.stdout.write("Stopping Crontab Service            [stopped]\n");
        sys.stdout.flush();

        ##return
        return(True);

    else:

        ##run destroy() func
        crontab.destroy();

        ##system output
        sys.stdout.write("Stopping Crontab Service            [stopped]\n");
        sys.stderr.write("Service Alreally Stopped\n");
        sys.stdout.flush();
        sys.stderr.flush();

        ##return False
        return(False);

##service_status
def service_status():

    ##global values
    global LOCK_FP;

    ##read lock_stat
    lock_stat=kglobal.lock_init(LOCK_FP);

    ##get pidlst
    pidlst=kglobal.get_pidlst(PROC_NAME);

    ##if is running and lock is set
    if (str(pidlst) != "") and (int(lock_stat) == kglobal.LOCK_ST):

        ##system print
        sys.stdout.write("Service is Running\n");
        sys.stdout.flush();

        ##exit proc
        sys.exit(0);

    ##if is running and lock is unset
    elif (str(pidlst) != "") and (int(lock_stat) == kglobal.LOCK_US):

        ##system print
        sys.stderr.write("Service Still Running But Lock is Free\n");
        sys.stderr.flush();

        ##exit proc
        sys.exit(1);

    ##if is not running and lock is set
    elif (str(pidlst) == "") and (int(lock_stat) == kglobal.LOCK_ST):

        ##system print
        sys.stderr.write("Service is Not Running But Lock is Locked\n");
        sys.stderr.flush();

        ##exit proc
        sys.exit(3);

    ##if is not running and lock is unset
    else:

        ##system print
        sys.stderr.write("Service Alreally Stopped\n");
        sys.stderr.flush();

        ##exit proc
        sys.exit(4);

##usage function
def usage():

    ##system print
    sys.stdout.write(sys.argv[0] + " [start|stop|restart|status]\n");
    sys.stdout.flush();

    ##return
    return(True);

##run function
def main():

    ##to get and aly the argv1, if error print usage
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

    ##return
    return(True);

##main function
if __name__ == "__main__":

    ##call main() func
    main();

    ##exit proc
    sys.exit(0);

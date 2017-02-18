###############################################################################
## Service.Py
## the crontab service function
## Written By Kyle Chen
## Version 20170218v1
## Note:
##  a service struct to run crontab
##  to use less mem and cpus
###############################################################################
#!/usr/bin/env python

##import pkgs
import kglobal;
import crontab;
import time;
import sys;

##init kglobal values
WORK_PTH=kglobal.get_wpth();
CFG_PTH=WORK_PTH + "/etc";
GLOBAL_CFG_FP=CFG_PTH + "/service.cfg";
SLEEP_INTERVAL=0;

##service_init
def service_init():

    global SLEEP_INTERVAL;

    kglobal.file_init(GLOBAL_CFG_FP);
    SLEEP_INTERVAL=int(kglobal.get_gval("SLEEP_INTERVAL",GLOBAL_CFG_FP));

    return(True);

##service_destroy
def service_destroy():

    global SLEEP_INTERVAL;

    SLEEP_INTERVAL=0;

    return(True);

##run function
def main():

    global SLEEP_INTERVAL;

    service_init();

    crontab.main();
    time.sleep(float(SLEEP_INTERVAL));

    service_destroy();
    return(True);

##main function
if __name__ == "__main__":

    while True:
        main();

    sys.exit(0);

###############################################################################
## Crontab.Py
## the main crontab run function
## Written By Kyle Chen
## Version 201700309v1
## Note:
##  Add AIX Support
###############################################################################
#!/usr/bin/env python

##import pkgs
import kglobal;
import sys;
import re;
import os;
import time;
import gc;
import logging;
import multiprocessing;

##define kglobal values
WORK_PTH=kglobal.get_wpth();
BIN_PTH=WORK_PTH + "/bin";
CFG_PTH=WORK_PTH + "/etc";
LIB_PTH=WORK_PTH + "/lib";
LOG_PTH=WORK_PTH + "/log";
LOCK_PTH=WORK_PTH + "/lock";
GLOBAL_CFG_FP=CFG_PTH + "/global.cfg";
CRONTAB_CFG_FP=CFG_PTH + "/crontab.cfg";
LOG_FP=LOG_PTH + "/crontab.log";
LOG_NOHUP_FP=LOG_PTH + "/nohup.log";
LOCK_FP=LOCK_PTH + "/crontab.lock";
DEBUG_PRT="";
CRON_CONT="";
CRON_LINENUM=0;
CRON_LIST=[];
MIN_LIST=[];
HOUR_LIST=[];
DAY_LIST=[];
MONTH_LIST=[];
WEEK_LIST=[];
USR_LIST=[];
COMM_LIST=[];
MIN_NOW="";
HOUR_NOW="";
DAY_NOW="";
MONTH_NOW="";
WEEK_NOW="";
LOG_MAX_SIZE=0;
LOG_LEVEL="";
LOCK_STAT=0;
LOG_SIZE=0;
LOG_NOHUP_SIZE=0;
SLEEP_INTERVAL=0;
BIN_FP="crontab.py";
PROC_PID=0;

##aly crontab.cfg
def aly_croncfg():

    ##global values
    global CRON_LINENUM;
    global MIN_LIST;
    global HOUR_LIST;
    global DAY_LIST;
    global MONTH_LIST;
    global WEEK_LIST;
    global USR_LIST;
    global COMM_LIST;
    global CRON_LIST;

    ##priviate values
    linedt_list=[];
    linenum=0;
    linesize=0;
    count=0;

    ##read data from CRON_CONT, split to list and remove Null values
    CRON_LIST=CRON_CONT.split("\n");
    CRON_LIST.remove("");

    ##info log
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab CFG Reading");

    ##read data from CRON_LIST line by line
    for linedt in CRON_LIST:

        ##replace multi spaces into one space
        linedt=re.sub(r"\ +"," ",linedt);

        ##split linedt to list with space
        linedt_list=linedt.split(" ");

        ##get the size of linedt_list, which the items in one line
        linesize=len(linedt_list);

        ##to check the linesize is legal, if not just continue
        if linesize < 7:
            continue;

        ##split and append to list
        MIN_LIST.append(linedt_list[0]);
        HOUR_LIST.append(linedt_list[1]);
        DAY_LIST.append(linedt_list[2]);
        MONTH_LIST.append(linedt_list[3]);
        WEEK_LIST.append(linedt_list[4]);
        USR_LIST.append(linedt_list[5]);
        COMM_LIST.append(linedt_list[6]);

        ##if the CMD field is only one command, just continue
        if linesize == 7:
            linenum+=1;
            continue;

        ##if the CMD field is more than one command, just save it in one COMM_LIST value
        count=7;
        while count < linesize:
            COMM_LIST[linenum]=COMM_LIST[linenum] + " " + linedt_list[count];
            count+=1;

        ##ok, this line aly done, just save as a legal line and continue
        linenum+=1;

    ##let CRON_LINENUM become a legal linenum
    CRON_LINENUM=linenum;

    ##write into log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab CFG Read Done");

    ##return value
    return(True);

##prt cron cfg
def prt_croncfg():

    ##priviate values
    linenum=0;

    ##just print values line by line
    while linenum < CRON_LINENUM:
    
        sys.stdout.write("%s %s %s %s %s %s %s\n" % (MIN_LIST[linenum], HOUR_LIST[linenum], DAY_LIST[linenum], MONTH_LIST[linenum], WEEK_LIST[linenum], USR_LIST[linenum], COMM_LIST[linenum]));
        sys.stdout.flush();

        linenum+=1;

    ##return value
    return(True);

##check min val
def check_croncfg():
     
    ##global values
    global CRON_LINENUM;
    global MIN_LIST;
    global HOUR_LIST;
    global DAY_LIST;
    global MONTH_LIST;
    global WEEK_LIST;

    ##priviate values
    linenum=0;

    ##create pattern to match the time
    min_pattern=re.compile(r"^(\d+[,\d]*|\*)$");
    hour_pattern=re.compile(r"^(\d+[,\d]*|\*)$");
    day_pattern=re.compile(r"^(\d+[,\d]*|\*)$");
    month_pattern=re.compile(r"^(\d+[,\d]*|\*)$");
    week_pattern=re.compile(r"^(\d+[,\d]*|\*)$");

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab CFG Checking");

    ##ok, lets check it line by line
    while linenum < CRON_LINENUM:

        ##get the pattern result list
        flag_min=min_pattern.findall(MIN_LIST[linenum]);
        flag_hour=hour_pattern.findall(HOUR_LIST[linenum]);
        flag_day=day_pattern.findall(DAY_LIST[linenum]);
        flag_month=month_pattern.findall(MONTH_LIST[linenum]);
        flag_week=week_pattern.findall(WEEK_LIST[linenum]);

        ##get the size of result list
        size_min=len(flag_min);
        size_hour=len(flag_hour);
        size_day=len(flag_day);
        size_month=len(flag_month);
        size_week=len(flag_week);

        ##check all field from size of the result
        if ( size_min == 1 ) and ( size_hour == 1 ) and ( size_day == 1 ) and (size_month == 1 ) and ( size_week == 1 ):

            ##debug msg
            kglobal.prt_dbg("linenum", linenum, DEBUG_PRT);
            kglobal.prt_dbg("MIN_LIST", MIN_LIST[linenum], DEBUG_PRT);
            kglobal.prt_dbg("HOUR_LIST", HOUR_LIST[linenum], DEBUG_PRT);
            kglobal.prt_dbg("DAY_LIST", DAY_LIST[linenum], DEBUG_PRT);
            kglobal.prt_dbg("MONTH_LIST", MONTH_LIST[linenum], DEBUG_PRT);
            kglobal.prt_dbg("WEEK_LIST", WEEK_LIST[linenum], DEBUG_PRT);

            ##it means this line is legal
            linenum+=1;

            ##go next line
            continue;

        else:

            ##if not legal just del from the time lists
            del MIN_LIST[linenum];
            del HOUR_LIST[linenum];
            del DAY_LIST[linenum];
            del MONTH_LIST[linenum];
            del WEEK_LIST[linenum];
            del USR_LIST[linenum];
            del COMM_LIST[linenum];

            ##if means this line is not legal
            CRON_LINENUM-=1;

            ##go next line
            continue;

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab CFG Check Done");

    ##return value
    return(True);

##time cmp
##to compare a time field
def time_cmp(time_set, time_now):

    ##private values
    time_set=re.sub(r",+$","",time_set);
    time_lst=[time_set];
    lstsize=1;

    ##check multi pattern
    split_pattern=re.compile(r"(,)");
    flag_split=split_pattern.findall(time_set);
    size_split=len(flag_split);

    ##get multi pattern size
    if size_split >= 1:
        time_lst=time_set.split(",");
        lstsize=len(time_lst);
    
    ##check time and run
    i=0;
    while i < lstsize:
        ##if is now or "*" just return True, if not return False
        if ( time_lst[i] == time_now ) or ( time_lst[i] == "*" ):
            return True;
        i+=1;

    ##return value
    return False;

##run cron
def run_cron():

    ##global values
    global LOCK_STAT;

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Running");

    ##priviate values
    linenum = 0;

    ##just do it line by line
    while linenum < CRON_LINENUM:

        ##to check the time, if matched then start a proc to run it, if not just continue
        if (time_cmp(MIN_LIST[linenum], MIN_NOW)) and (time_cmp(HOUR_LIST[linenum], HOUR_NOW)) and (time_cmp(DAY_LIST[linenum], DAY_NOW)) and (time_cmp(MONTH_LIST[linenum], MONTH_NOW)) and (time_cmp(WEEK_LIST[linenum], WEEK_NOW)):

            ##run as a new proc background
            ##set the run function and the argvs
            ppr = multiprocessing.Process(target = run_cmd, args = (USR_LIST[linenum], COMM_LIST[linenum]));
            ##start run it
            ppr.start();

            ##write log file
            kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "[" + str(ppr.pid) + "][" + str(ppr.name) + "][" + str(ppr.is_alive()) + "]");

        ##ok, next line
        linenum+=1;

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Done");

    ##return value
    return(True);

##run cmd
def run_cmd(username, command):

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Running Command");

    ##to check the command, if there is a "\" to change into "\\\", if not the command will be something wrong
    command=re.sub(r"\"","\\\"", command);

    ##set to background mode and packed into cmd
    cmd="su - " + username + " -c \"" + command + "\" &";

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "[CMD] " + cmd);

    ##debug print
    kglobal.prt_dbg("cmd", cmd, DEBUG_PRT);

    ##ok, run it
    os.system(cmd);

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Run [" + cmd + "] Done");

    ##return value
    return(True);

##cron_init
def cron_init():

    ##global values
    global CRON_CONT;
    global MIN_NOW;
    global HOUR_NOW;
    global DAY_NOW;
    global MONTH_NOW;
    global WEEK_NOW;
    global LOG_SIZE;
    global LOG_NOHUP_SIZE;

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Log Rotate Starting");

    ##crontab.log rotate
    if kglobal.file_init(LOG_FP):
        LOG_SIZE=kglobal.file_size(LOG_FP) / 1024 / 1024;
    log_rotate(LOG_FP, LOG_SIZE);

    ##nohup.out rotate
    if kglobal.file_init(LOG_NOHUP_FP):
        LOG_NOHUP_SIZE=kglobal.file_size(LOG_NOHUP_FP) / 1024 / 1024;
    log_rotate(LOG_NOHUP_FP, LOG_NOHUP_SIZE);

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Log Rotate Done");

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Getting Systime");

    ##read crontab.cfg into CRON_CONT
    CRON_CONT=kglobal.read_file(CRONTAB_CFG_FP);

    ##get systime into global values
    (MIN_NOW, HOUR_NOW, DAY_NOW, MONTH_NOW, WEEK_NOW) = kglobal.get_systime();

    ##debug print
    kglobal.prt_dbg("MIN_NOW", MIN_NOW, DEBUG_PRT);
    kglobal.prt_dbg("HOUR_NOW", HOUR_NOW, DEBUG_PRT);
    kglobal.prt_dbg("DAY_NOW", DAY_NOW, DEBUG_PRT);
    kglobal.prt_dbg("MONTH_NOW", MONTH_NOW, DEBUG_PRT);
    kglobal.prt_dbg("WEEK_NOW", WEEK_NOW, DEBUG_PRT);
    kglobal.prt_dbg("DEBUG_PRT", DEBUG_PRT, DEBUG_PRT);

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Get Systime Done");

    ##call aly_croncfg();
    aly_croncfg();

    ##call check_croncfg();
    check_croncfg();

    ##print croncfg
    prt_croncfg();

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Initial Done");

    ##return value
    return(True);

##log rotate
##if logfile larger or equal LOG_MAX_SIZE just rotate it
##rotate it only once
def log_rotate(fp, size):

    ##global values
    global LOG_SIZE;
    global LOG_MAX_SIZE;

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Log Set Starting");

    ##debug print
    kglobal.prt_dbg("LOG_SIZE", size, DEBUG_PRT);
    kglobal.prt_dbg("LOG_MAX_SIZE", LOG_MAX_SIZE, DEBUG_PRT);

    ##check LOG_SIZE
    if size >= LOG_MAX_SIZE:
        
        ##if LOG_SIZE is lager than LOG_MAX_SIZE setting, just mv it to a backup log
        kglobal.file_mv(fp, fp + ".old");

        ##create a new blank log file
        kglobal.file_init(fp);

        ##reset LOG_SIZE
        LOG_SIZE=0;

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Log Set Done");

    ##return value
    return(True);

##cron_destroy
def cron_destroy():

    ##global values
    global CRON_CONT;
    global CRON_LINENUM;
    global CRON_LIST;
    global MIN_LIST;
    global HOUR_LIST;
    global DAY_LIST;
    global MONTH_LIST;
    global WEEK_LIST;
    global USR_LIST;
    global COMM_LIST;
    global MIN_NOW;
    global HOUR_NOW;
    global DAY_NOW;
    global MONTH_NOW;
    global WEEK_NOW;
    global LOG_SIZE;
    global LOG_NOHUP_SIZE;

    ##to set them Null
    CRON_CONT="";
    CRON_LINENUM=0;
    CRON_LIST=[];
    MIN_LIST=[];
    HOUR_LIST=[];
    DAY_LIST=[];
    MONTH_LIST=[];
    WEEK_LIST=[];
    USR_LIST=[];
    COMM_LIST=[];
    MIN_NOW="";
    HOUR_NOW="";
    DAY_NOW="";
    MONTH_NOW="";
    WEEK_NOW="";
    LOG_SIZE=0;
    LOG_NOHUP_SIZE=0;

    ##free the mem
    gc.collect();

    ##return value
    return(True);

##env init
def init():
    
    ##global values
    global DEBUG_PRT;
    global LOG_MAX_SIZE;
    global LOCK_STAT;
    global LOG_LEVEL;
    global SLEEP_INTERVAL;
    global PROC_PID;

    ##initial dirs
    kglobal.dir_init(BIN_PTH);
    kglobal.dir_init(CFG_PTH);
    kglobal.dir_init(LIB_PTH);
    kglobal.dir_init(LOG_PTH);
    kglobal.dir_init(LOCK_PTH);

    ##initial files
    kglobal.file_init(GLOBAL_CFG_FP);
    kglobal.file_init(CRONTAB_CFG_FP);

    ##read setting from global.cfg
    LOG_MAX_SIZE=int(kglobal.get_gval("LOG_MAX_SIZE",GLOBAL_CFG_FP));
    DEBUG_PRT=kglobal.get_gval("DEBUG_PRT",GLOBAL_CFG_FP);
    SLEEP_INTERVAL=kglobal.get_gval("SLEEP_INTERVAL",GLOBAL_CFG_FP);
    LOG_LEVEL=kglobal.get_gval("LOG_LEVEL",GLOBAL_CFG_FP);
    LOG_LEVEL=kglobal.get_loglevel(LOG_LEVEL);

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Initialing");

    ##get pidlist and del the last space
    pidlst=kglobal.get_pidlst(BIN_FP);

    ##get PROC_PID
    PROC_PID=os.getpid();

    ##if there is not only one proc
    if (str(PROC_PID) != str(pidlst)) and (str(pidlst) != ""):

        ##write log file
        kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_ERROR, "Crontab Proc Alreally Running");

        ##debug print
        kglobal.prt_dbg("ERROR", "Crontab Proc Alreally Running", DEBUG_PRT);

        ##exit this proc
        sys.exit(1);

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Lock Setting");

    ##initial lock file
    kglobal.file_init(LOCK_FP);

    ##read LOCK_STAT from lock file
    LOCK_STAT=kglobal.lock_init(LOCK_FP);
    if LOCK_STAT == "":
        LOCK_STAT=kglobal.LOCK_US;

    ##debug print
    kglobal.prt_dbg("LOCK_STAT", LOCK_STAT, DEBUG_PRT);

    ##set lock into locked mode
    LOCK_STAT=kglobal.lock_set(LOCK_STAT);

    ##debug print
    kglobal.prt_dbg("LOCK_STAT", LOCK_STAT, DEBUG_PRT);

    ##write into lock file
    kglobal.lock_write(LOCK_FP, LOCK_STAT);

    ##debug print
    kglobal.prt_dbg("LOCK_STAT", LOCK_STAT, DEBUG_PRT);

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Lock Set Done");
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Log Initialing");

    ##write log file
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Log Initial Done");
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "[Crontab.py PID] " + kglobal.get_pidlst(BIN_FP));

    ##return value
    return(True);

##global destroy
def destroy():

    ##global values
    global LOCK_STAT;

    ##set LOCK_STAT into unset mode
    LOCK_STAT=kglobal.lock_unset(LOCK_STAT);

    ##debug print
    kglobal.prt_dbg("LOCK_STAT", LOCK_STAT, DEBUG_PRT);

    ##write into lock file
    kglobal.lock_write(LOCK_FP, str(LOCK_STAT));

    ##return value
    return(True);

##run function
def main():

    ##call cron_init();
    cron_init();

    ##call run_cron();
    run_cron();

    ##call cron_destroy();
    cron_destroy();

    ##sleep for a while
    time.sleep(float(SLEEP_INTERVAL));

    ##return value
    return(True);

##main function
if __name__ == "__main__":

    ##global initial, call init()
    init();

    ##create a infinite loop
    while True:

        ##call main()
        main();

    ##exit proc
    sys.exit(0);

###############################################################################
## Crontab.Py
## the main crontab run function
## Written By Kyle Chen
## Version 20170218v1
## Note:
##  try to use popen() run cmd but failed after test it cant run background
##  change to use Service.py monitor
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

##init kglobal values
WORK_PTH=kglobal.get_wpth();
BIN_PTH=WORK_PTH + "/bin";
CFG_PTH=WORK_PTH + "/etc";
LIB_PTH=WORK_PTH + "/lib";
LOG_PTH=WORK_PTH + "/log";
LOCK_PTH=WORK_PTH + "/lock";
GLOBAL_CFG_FP=CFG_PTH + "/global.cfg";
CRONTAB_CFG_FP=CFG_PTH + "/crontab.cfg";
LOG_FP=LOG_PTH + "/crontab.log";
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

##aly crontab.cfg
def aly_croncfg():

    global CRON_LINENUM;
    global MIN_LIST;
    global HOUR_LIST;
    global DAY_LIST;
    global MONTH_LIST;
    global WEEK_LIST;
    global USR_LIST;
    global COMM_LIST;
    global CRON_LIST;
    linedt_list=[];
    linenum=0;
    linesize=0;
    count=0;
    CRON_LIST=CRON_CONT.split("\n");
    CRON_LIST.remove("");

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab CFG Reading");
    
    for linedt in CRON_LIST:

        linedt=re.sub(r"\ +"," ",linedt);
        linedt_list=linedt.split(" ");
        linesize=len(linedt_list);

        if linesize < 7:
            continue;

        MIN_LIST.append(linedt_list[0]);
        HOUR_LIST.append(linedt_list[1]);
        DAY_LIST.append(linedt_list[2]);
        MONTH_LIST.append(linedt_list[3]);
        WEEK_LIST.append(linedt_list[4]);
        USR_LIST.append(linedt_list[5]);
        COMM_LIST.append(linedt_list[6]);

        if linesize == 7:
            linenum+=1;
            continue;

        count=7;
        while count < linesize:
            COMM_LIST[linenum]=COMM_LIST[linenum] + " " + linedt_list[count];
            count+=1;

        count+=1;
        linenum+=1;

    CRON_LINENUM=linenum;

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab CFG Read Done");
    return(True);

##prt cron cfg
def prt_croncfg():

    linenum=0;
    while linenum < CRON_LINENUM:
    
        sys.stdout.write("%s %s %s %s %s %s %s\n" % (MIN_LIST[linenum], HOUR_LIST[linenum], DAY_LIST[linenum], MONTH_LIST[linenum], WEEK_LIST[linenum], USR_LIST[linenum], COMM_LIST[linenum]));
        sys.stdout.flush();

        linenum+=1;

    return(True);

##check min val
def check_croncfg():
     
    global CRON_LINENUM;
    global MIN_LIST;
    global HOUR_LIST;
    global DAY_LIST;
    global MONTH_LIST;
    global WEEK_LIST;

    linenum=0;

    min_pattern=re.compile(r"^([0-9]|[0-5][0-9]|\*)$");
    hour_pattern=re.compile(r"^([0-9]|[0-1][0-9]|2[0-4]|\*)$");
    day_pattern=re.compile(r"^([0-9]|[0-2][0-9]|3[0-1]|\*$)");
    month_pattern=re.compile(r"^([0-9]|0[0-9]|1[0-2]|\*$)");
    week_pattern=re.compile(r"^([0-7]|\*$)");

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab CFG Checking");

    while linenum < CRON_LINENUM:

        flag_min=min_pattern.findall(MIN_LIST[linenum]);
        flag_hour=hour_pattern.findall(HOUR_LIST[linenum]);
        flag_day=day_pattern.findall(DAY_LIST[linenum]);
        flag_month=month_pattern.findall(MONTH_LIST[linenum]);
        flag_week=week_pattern.findall(WEEK_LIST[linenum]);

        size_min=len(flag_min);
        size_hour=len(flag_hour);
        size_day=len(flag_day);
        size_month=len(flag_month);
        size_week=len(flag_week);

        if ( size_min == 1 ) and ( size_hour == 1 ) and ( size_day == 1 ) and (size_month == 1 ) and ( size_week == 1 ):

            kglobal.prt_dbg("linenum", linenum, DEBUG_PRT);
            kglobal.prt_dbg("MIN_LIST", MIN_LIST[linenum], DEBUG_PRT);
            kglobal.prt_dbg("HOUR_LIST", HOUR_LIST[linenum], DEBUG_PRT);
            kglobal.prt_dbg("DAY_LIST", DAY_LIST[linenum], DEBUG_PRT);
            kglobal.prt_dbg("MONTH_LIST", MONTH_LIST[linenum], DEBUG_PRT);
            kglobal.prt_dbg("WEEK_LIST", WEEK_LIST[linenum], DEBUG_PRT);

            linenum+=1;
            continue;

        else:

            del MIN_LIST[linenum];
            del HOUR_LIST[linenum];
            del DAY_LIST[linenum];
            del MONTH_LIST[linenum];
            del WEEK_LIST[linenum];
            del USR_LIST[linenum];
            del COMM_LIST[linenum];

            CRON_LINENUM-=1;
            continue;

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab CFG Check Done");
    return(True);

##time cmp
def time_cmp(time_set, time_now):
    
    if ( time_set == time_now ) or ( time_set == "*" ):
        return True;
    else:
        return False;

##run cron
def run_cron():

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Running");
    if LOCK_STAT == False:
        return(False);
    
    linenum = 0;
    while linenum < CRON_LINENUM:

        if (time_cmp(MIN_LIST[linenum], MIN_NOW)) and (time_cmp(HOUR_LIST[linenum], HOUR_NOW)) and (time_cmp(DAY_LIST[linenum], DAY_NOW)) and (time_cmp(MONTH_LIST[linenum], MONTH_NOW)) and (time_cmp(WEEK_LIST[linenum], WEEK_NOW)):
            ppr = multiprocessing.Process(target = run_cmd, args = (USR_LIST[linenum], COMM_LIST[linenum]));
            ppr.start();
            kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "[" + str(ppr.pid) + "][" + str(ppr.name) + "][" + str(ppr.is_alive()) + "]");

        linenum+=1;

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Done");
    return(True);

##run cmd
def run_cmd(username, command):

    #rlst=[];
    #result="";
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Running Command");
    command=re.sub(r"\"","\\\"", command);
    cmd="su - " + username + " -c \"" + command + "\" &";
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "[CMD] " + cmd);
    kglobal.prt_dbg("cmd", cmd, DEBUG_PRT);
    #rlst=os.popen(cmd);
    #result=('').join(rlst);
    #result=re.sub(r"\n","",result);
    #kglobal.prt_dbg("result", result, DEBUG_PRT);
    #kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "[RUN] " + result);
    #rlst.close();
    os.system(cmd);
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Run [" + cmd + "] Done");
    return(True);

##cron_init
def cron_init():

    global DEBUG_PRT;
    global LOG_MAX_SIZE;
    global CRON_CONT;
    global MIN_NOW;
    global HOUR_NOW;
    global DAY_NOW;
    global MONTH_NOW;
    global WEEK_NOW;
    global LOCK_STAT;
    global LOG_SIZE;
    global LOG_LEVEL;

    kglobal.dir_init(BIN_PTH);
    kglobal.dir_init(CFG_PTH);
    kglobal.dir_init(LIB_PTH);
    kglobal.dir_init(LOG_PTH);
    kglobal.dir_init(LOCK_PTH);
    kglobal.file_init(GLOBAL_CFG_FP);
    kglobal.file_init(CRONTAB_CFG_FP);

    LOG_MAX_SIZE=int(kglobal.get_gval("LOG_MAX_SIZE",GLOBAL_CFG_FP));
    DEBUG_PRT=kglobal.get_gval("DEBUG_PRT",GLOBAL_CFG_FP);
    CRON_CONT=kglobal.read_file(CRONTAB_CFG_FP);
    LOG_LEVEL=kglobal.get_gval("LOG_LEVEL",GLOBAL_CFG_FP);

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Initialing");

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Lock Setting");
    kglobal.file_init(LOCK_FP);
    LOCK_STAT=kglobal.lock_init(LOCK_FP);
    kglobal.prt_dbg("LOCK_STAT", LOCK_STAT, DEBUG_PRT);
    LOCK_STAT=kglobal.lock_set(LOCK_STAT);
    kglobal.prt_dbg("LOCK_STAT", LOCK_STAT, DEBUG_PRT);
    kglobal.lock_write(LOCK_FP, LOCK_STAT);
    kglobal.prt_dbg("LOCK_STAT", LOCK_STAT, DEBUG_PRT);
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Lock Set Done");

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Log Initialing");
    if kglobal.file_init(LOG_FP):
        LOG_SIZE=kglobal.file_size(LOG_FP) / 1024 / 1024;
    log_rotate();
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Log Initial Done");

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Getting Systime");
    (MIN_NOW, HOUR_NOW, DAY_NOW, MONTH_NOW, WEEK_NOW) = kglobal.get_systime();
    kglobal.prt_dbg("MIN_NOW", MIN_NOW, DEBUG_PRT);
    kglobal.prt_dbg("HOUR_NOW", HOUR_NOW, DEBUG_PRT);
    kglobal.prt_dbg("DAY_NOW", DAY_NOW, DEBUG_PRT);
    kglobal.prt_dbg("MONTH_NOW", MONTH_NOW, DEBUG_PRT);
    kglobal.prt_dbg("WEEK_NOW", WEEK_NOW, DEBUG_PRT);
    kglobal.prt_dbg("DEBUG_PRT", DEBUG_PRT, DEBUG_PRT);
    kglobal.prt_dbg("LOG_MAX_SIZE", LOG_MAX_SIZE, DEBUG_PRT);
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Get Systime Done");

    aly_croncfg();
    check_croncfg();
    #prt_croncfg();

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Initial Done");
    return(True);

##log rotate
##if logfile larger or equal LOG_MAX_SIZE just rotate it
##rotate it only once
def log_rotate():

    global LOG_SIZE;
    global LOG_MAX_SIZE;

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Log Rotating");

    kglobal.prt_dbg("LOG_SIZE", LOG_SIZE, DEBUG_PRT);
    kglobal.prt_dbg("LOG_MAX_SIZE", LOG_MAX_SIZE, DEBUG_PRT);

    if LOG_SIZE >= LOG_MAX_SIZE:
        kglobal.file_mv(LOG_FP, LOG_FP + ".old");
        kglobal.file_init(LOG_FP);
        LOG_SIZE=0;

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Log Rotate Done");
    return(True);

##cron_destroy
def cron_destroy():

    global DEBUG_PRT;
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
    global LOG_MAX_SIZE;
    global LOG_LEVEL;
    global LOCK_STAT;

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Destroy Initialing");

    LOCK_STAT=kglobal.lock_unset(LOCK_STAT);
    kglobal.prt_dbg("LOCK_STAT", LOCK_STAT, DEBUG_PRT);
    kglobal.lock_write(LOCK_FP, str(LOCK_STAT));

    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "Crontab Destroy Done");

    DEBUG_PRT="";
    LOG_MAX_SIZE=0;
    LOG_LEVEL="";
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

    gc.collect();
    return(True);

##run function
def main():

    cron_init();
    kglobal.log_msg(LOG_FP, LOG_LEVEL, kglobal.LOG_MSG_INFO, "[Crontab.py PID] " + kglobal.get_pidlst("crontab.py"));
    run_cron();
    cron_destroy();

    return(True);

##main function
if __name__ == "__main__":

    main();
    sys.exit(0);

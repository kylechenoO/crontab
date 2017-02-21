###############################################################################
## Kglobal.Py
## some global funcs
## Written By Kyle Chen
## Version 20170221v1
## Note:
##  optimize some funcs
###############################################################################
#!/usr/bin/env python

##import pkgs
import os;
import sys;
import re;
import time;
import shutil;
import logging;

##def global values
NULL="Null";
LOCK_ST=1;
LOCK_US=0;
LOG_LEVEL_INFO=logging.INFO;
LOG_LEVEL_WARNING=logging.WARNING;
LOG_LEVEL_DEBUG=logging.DEBUG;
LOG_LEVEL_ERROR=logging.ERROR;
LOG_LEVEL_CRITICAL=logging.CRITICAL;
LOG_MSG_INFO="info";
LOG_MSG_WARNING="warning";
LOG_MSG_DEBUG="debug";
LOG_MSG_ERROR="error";
LOG_MSG_CRITICAL="critical";

##get work path
##return work_path
def get_wpth():

    result="";
    pth=re.split(r"\/", sys.path[0]);
    max_index=len(pth)-2;
    i=0;

    while i < max_index:
        result+=pth[i] + "/";
        i+=1;

    result+=pth[i];
    return(result);

##read file
##return file content
def read_file(file_name):
    
    result="";
    flag="";
    size="";

    com_pattern=re.compile("^#");
    fp=open(file_name);

    while True:
        line=fp.readline();
        flag=com_pattern.findall(line);
        size=len(flag);
        if size > 0:
            continue;
        if not line:
            break;
        result+=line;

    fp.close();
    return(result);

##get global cfg val
##return value for the var
def get_gval(var, file_name):

    result="";
    linedt="";
    flag="";
    size="";
    val=NULL;

    pattern=re.compile("^" + var + "\ *=.*$");
    fp=open(file_name);

    while True:
        line=fp.readline();
        flag=pattern.findall(line);
        size=len(flag);
        if size > 0:
            val=re.sub(r"^.*=\ *","",line);
            val=re.sub(r"\n","",val);
        if not line:
            break;

    fp.close();
    return(val);

##prt_dbg
##return flag
def prt_dbg(var, val, flag):

    if flag == "True":
        sys.stdout.write("DEBUG PRT:[%s] is [%s]\n" % (var, str(val)));
        sys.stdout.flush();

    return(flag);

##get_systime
##return values
##  MIN HOUR DAY MONTH WEEKDAY
def get_systime():

    timestamp=time.strftime('%M %H %d %m %w',time.localtime(time.time()));
    ts=re.split(r" ", timestamp);
    return(ts[0], ts[1],ts[2], ts[3], ts[4]);

##dir_init
##to check dir exiest if not just create it
##return True or False
def dir_init(dir_name):

    if os.path.isdir(dir_name):
        return True;
    else:
        os.mkdir(dir_name, 0755);
        return False;

##file_init
##to check file exiest if not just create it
##return True
def file_init(file_name):
    if os.path.isfile(file_name):
        return True;
    else:
        fp = open(file_name, 'w')
        fp.close();
        return False;

##file_size
##return file_size
def file_size(file_name):
    return os.path.getsize(file_name);

##file_cp
##copy a file
def file_cp(src, dst):
    shutil.copy(src, dst);
    return(True);

##file_rm
##remove a file
def file_rm(file_name):
    os.remove(file_name);
    return(True);

##file_mv
##move or rename a file
def file_mv(src, dst):
    if os.path.isfile(dst):
        os.remove(dst);
        shutil.copy(src, dst);
    else:
        shutil.copy(src, dst);
        os.remove(src);
    return(True);

##lock_init
##initial lock status
def lock_init(fp_lock):
    result="";
    fp=open(fp_lock);
    result=fp.read(1);
    fp.close();
    return(result);

##lock_write
##write key into lock file
def lock_write(fp_lock, key):
    fp=open(fp_lock, "w");
    fp.write(str(key));
    fp.close();
    return(True);

##lock_set
##set lock status
def lock_set(lock_stat):
    if (lock_stat != "") or (int(lock_stat) == LOCK_ST):
        sys.stdout.write("LOCK EXIST.!");
        sys.stdout.flush();

    return(LOCK_ST);

##lock_unset
##unset lock status
def lock_unset(lock_stat):
    return(LOCK_US);

##log_msg
##log msg prt and to file
def log_msg(fp_log , log_level, msg_level, msg):
    logging.basicConfig(filename=fp_log, format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%Y-%m-%d %I:%M:%S', level=log_level);
    if msg_level == LOG_MSG_INFO:
        logging.info(str(msg));
    elif msg_level == LOG_MSG_WARNING:
        logging.warning(str(msg));
    elif msg_level == LOG_MSG_DEBUG:
        logging.debug(str(msg));
    elif msg_level == LOG_MSG_ERROR:
        logging.error(str(msg));
    elif msg_level == LOG_MSG_CRITICAL:
        logging.critical(str(msg));
    else:
        logging.debug(str(msg));
    return(True);

##get_pidlst
##get the proc pid list
def get_pidlst(proc):
    rlst=[];
    result="";

    rlst=os.popen("ps aux | awk '/python/ && /%s$/{ printf(\"%%s \", $2); }'" % (proc));
    result=('').join(rlst);
    result=re.sub(r"\n","",result);
    rlst.close();

    return(result);

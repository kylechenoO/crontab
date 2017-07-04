'''
    Crontab.py Lib
    Written By Kyle Chen
    Version 20170628v1
'''

##import buildin pkgs
import re
import time
import threading

##import lib
from RunCmd import RunCmd

##thread lock
##set thread lock
LOCK = threading.Lock()

##Crontab Class
class Crontab:

    ##initial function
    def __init__(self, crontab_cfg_file, logger, max_threads, \
                    thread_timeout, subproc_limits, max_retry, thread_delay):

        self.logger = logger
        self.max_threads = max_threads
        self.thread_timeout = thread_timeout
        self.LOCK = LOCK
        self.SUBPROC_LIMITS = subproc_limits
        self.MAX_RETRY = max_retry
        self.THREAD_DELAY = thread_delay

        self.logger.debug("[MAX_THREADS][%s]" % (self.max_threads))

	self.crontab_clst = self.crontab_readcfg(crontab_cfg_file)
	for line in self.crontab_clst:
	    self.logger.debug('[%s]' % (line))

        (self.SEC_NOW, self.MIN_NOW, \
                self.HOR_NOW, self.DAY_NOW, \
                self.MON_NOW, self.WEK_NOW) = self.crontab_getsystime()
        self.logger.debug("[%s-%s %s %s:%s:%s]" %(self.MON_NOW, self.DAY_NOW, \
                            self.WEK_NOW, self.HOR_NOW, self.MIN_NOW, self.SEC_NOW))

        self.cfg_counts = self.crontab_cfg2arr(self.crontab_clst)
        self.logger.debug('[cfg_counts][%s]' % (self.cfg_counts))

	return(None)

    ##read crontab.cfg
    def crontab_readcfg(self, crontab_cfg_file):

	crontab_content=self.crontab_read_file(crontab_cfg_file)
	crontab_clst=crontab_content.split("\n")
	crontab_clst.remove("")

	return(crontab_clst)

    ##read_file func
    def crontab_read_file(self, file_name):

	result=""
	flag=""
	size=""

	com_pattern=re.compile("^#")
	fp=open(file_name)

	while True:
	    line=fp.readline()
	    flag=com_pattern.findall(line)
	    size=len(flag)

	    if size > 0:
		continue

	    if not line:
		break

	    result+=line

	fp.close()
	return(result)

    ##getsystime and return
    def crontab_getsystime(self):

        timestamp=time.strftime('%S %M %H %d %m %w',time.localtime(time.time()))
        ts=re.split(r" ", timestamp)

        return(ts[0], ts[1],ts[2], ts[3], ts[4], ts[5])

    ##to check time
    def crontab_checktime(self, num):

        strn = str(num)
        if strn[:1].isdigit() or strn[:1] == '*':

            return(True)

        else:

            self.logger.debug('[%s is not digit]' % (num))
            return(False)

    #convert crontab cfg to array
    def crontab_cfg2arr(self, crontab_clst):

        linenum = 0

        self.TIM_OUT = []
        self.SEC_LST = []
        self.MIN_LST = []
        self.HOR_LST = []
        self.DAY_LST = []
        self.MON_LST = []
        self.WEK_LST = []
        self.USR_LST = []
        self.COM_LST = []

        for linedt in crontab_clst:

            ##replace multi spaces into one space
            linedt = re.sub(r"\ +"," ",linedt)

            ##split linedt to list with space
            linedt_list = linedt.split(" ")

            ##get the size of linedt_list, which the items in one line
            linesize = len(linedt_list)

            ##to check the linesize is legal, if not just continue
            if linesize < 8:
                continue

            if not (self.crontab_checktime(linedt[0]) and self.crontab_checktime(linedt_list[1]) \
                        and self.crontab_checktime(linedt_list[2]) and self.crontab_checktime(linedt_list[3]) \
                        and self.crontab_checktime(linedt_list[4]) and self.crontab_checktime(linedt_list[5]) \
                        and self.crontab_checktime(linedt_list[6])):
                continue

            ##MAX_THREADS break
            if linenum >= self.max_threads:
                self.logger.error("[OUT OF MAX_THREADS]%s %s %s %s %s %s %s %s %s" % (linedt_list[0], linedt_list[1], \
                                    linedt_list[2], linedt_list[3], linedt_list[4], linedt_list[5], \
                                    linedt_list[6], linedt_list[7], linedt_list[8]))
                continue

            ##split and append to list
            self.TIM_OUT.append(linedt_list[0])
            self.SEC_LST.append(linedt_list[1])
            self.MIN_LST.append(linedt_list[2])
            self.HOR_LST.append(linedt_list[3])
            self.DAY_LST.append(linedt_list[4])
            self.MON_LST.append(linedt_list[5])
            self.WEK_LST.append(linedt_list[6])
            self.USR_LST.append(linedt_list[7])
            self.COM_LST.append(linedt_list[8])

            ##if the CMD field is only one command, just continue
            if linesize == 9:
                linenum += 1
                continue

            ##if the CMD field is more than one command, just save it in one COMM_LIST value
            count = 9
            while count < linesize:
                self.COM_LST[linenum] = self.COM_LST[linenum] + " " + linedt_list[count]
                count+=1

            ##ok, this line aly done, just save as a legal line and continue
            linenum+=1

        return(linenum)

    ##compare time func
    def crontab_timecmp(self, time_set, time_now):

        time_set = re.sub(r",+$","",time_set)
        time_lst = [time_set]
        lstsize = 1

        ##check multi pattern
        split_pattern = re.compile(r"(,)")
        flag_split = split_pattern.findall(time_set)
        size_split = len(flag_split)

        ##get multi pattern size
        if size_split >= 1:
            time_lst = time_set.split(",")
            lstsize = len(time_lst)

        ##check time and run
        i = 0
        while i < lstsize:

            ##if is now or "*" just return True, if not return False
            if (str(time_lst[i]) == str(int(time_now))) or (time_lst[i] == "*"):
                return True
            i += 1

        ##return value
        return False

    ##Run CMD
    def run(self):

        threads = []
        line = 0
        while line < self.cfg_counts:

            if (self.crontab_timecmp(self.SEC_LST[line], self.SEC_NOW)) and (self.crontab_timecmp(self.MIN_LST[line], self.MIN_NOW)) \
                    and (self.crontab_timecmp(self.HOR_LST[line], self.HOR_NOW)) and (self.crontab_timecmp(self.DAY_LST[line], self.DAY_NOW)) \
                    and (self.crontab_timecmp(self.MON_LST[line], self.MON_NOW)) and (self.crontab_timecmp(self.WEK_LST[line], self.WEK_NOW)):

                if self.TIM_OUT[line] == '*' :
                    self.TIM_OUT[line] = self.thread_timeout

                thread = RunCmd(self.logger, self.USR_LST[line], \
                                    self.COM_LST[line], int(self.TIM_OUT[line]), \
                                    self.LOCK, int(self.SUBPROC_LIMITS), int(self.MAX_RETRY), int(self.THREAD_DELAY))
                thread.start()
                threads.append(thread)

            line += 1

	return(None)

    ##destructor function
    def __del__(self):

	return(None)

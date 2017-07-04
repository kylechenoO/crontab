'''
    RunCmd.py Lib
    Written By Kyle Chen
    Version 20170628v1
'''

##import buildin pkgs
import os
import re
import time
import signal
import datetime
import threading
import subprocess

##RunCmd Class
class RunCmd(threading.Thread):

    ##initial function
    def __init__(self, logger, usr, cmd, thread_timeout, LOCK, subproc_limits, max_retry, thread_delay):

        threading.Thread.__init__(self, name=cmd)
        self.logger = logger
        self.usr = usr
        self.cmd = cmd
        self.thread_timeout = thread_timeout
        self.lock = LOCK
        self.SUBPROC_LIMITS = subproc_limits
        self.MAX_RETRY = max_retry
        self.THREAD_DELAY = thread_delay

	return(None)

    ##threading run func
    def run(self):

        cmd = self.cmd
        cmd=re.sub(r"\"","\\\"", cmd);
        cmd="su - " + self.usr + " -c \"" + cmd + "\"";

        timeout = self.thread_timeout
        subproc_flag = self.subproc_check()

        i = 1
        if not subproc_flag:

            while i <= self.MAX_RETRY:
                time.sleep(self.THREAD_DELAY)
                self.logger.error('[subproc][%s][Retry][%s]' % (cmd, i))
                subproc_flag = self.subproc_check()

                if not subproc_flag:
                    i += 1
                    continue

                else:
                    subproc_flag = True
                    break

        if not subproc_flag:
            self.logger.error('[subproc_check][%s][Still Running]' % (cmd))
            return(False)

        self.logger.debug('[RunCmd][thread_timeout][%s]' % (self.thread_timeout))
        start = datetime.datetime.now()
        self.logger.debug('[RunCmd][START][%s]' % (start))
        process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
        pid = process.pid
        self.logger.debug("[%s][%s][%s]" % (pid, cmd, start))
        now = datetime.datetime.now()

        errflag = False
        while (process.poll() is None):
            time.sleep(0.001)
            now = datetime.datetime.now()

            if (now - start).seconds >= self.thread_timeout:
                os.kill(pid, signal.SIGKILL)
                self.logger.error("[%s][Time Out Error]" %(cmd))
                errflag = True
                break

        self.logger.debug('[RunCmd][END][%s]' % (now))
        self.logger.debug('[RunCmd][Total][%s]' % ((now - start).seconds))

        if errflag:

            return(False)

        else:

            out = process.stdout.read().strip("\r").strip("\n")
            err = process.stderr.read().strip("\r").strip("\n")
            self.logger.info("[%s]%s" %(self.cmd, out))
            self.logger.info("[%s]%s" %(self.cmd, err))
            return(True)

    ##subproc check
    def subproc_check(self):

		count = 0
		subproc_limits = self.SUBPROC_LIMITS
		cmd = 'ps -elf'
		process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
		out = process.stdout.read().strip("\r").strip("\n")
		pattern = re.compile('(\ *%s)' % (self.cmd))

		for line in re.finditer(pattern, str(out)):
			count += 1

		self.logger.debug('[subproc_check][%s][count][%s]' % (self.cmd, count))

		if count > subproc_limits:
			return(False)

		return(True)

    ##destructor function
    def __del__(self):

	return(None)

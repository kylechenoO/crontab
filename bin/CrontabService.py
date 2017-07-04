'''
    CrontabService.py
    Written By Kyle Chen
    Version 20170628v1
'''

##import buildin pkgs
import sys
import re
import os
import time
import logging
from logging.handlers import RotatingFileHandler

##get workpath
workpath="";
pathlst=re.split(r"\/", sys.path[0]);
max_index=len(pathlst)-1;
i=0;

while i < max_index-1:
	workpath+=pathlst[i] + "/";
	i+=1;

workpath+=pathlst[i]

##append workpath to path
sys.path.append("%s/lib" % ( workpath ))

##import priviate pkgs
from Config import Config
from Crontab import Crontab
from Lock import Lock

##CrontabService Class
class CrontabService:

	##initial function
	def __init__(self):

		##set priviate values
		self.config = Config(workpath)
		self.pid = os.getpid()
		self.pname = 'CrontabService.py'

		##logger initial
		#self.logger_init(self.config.LOG_LEVEL, self.config.LOG_MAX_SIZE, self.config.LOG_BACKUP_COUNT, self.config.LOG_FILE)
		self.logger_init()

		##lock initial
		self.lockObj = Lock(self.pname, self.pid, self.config.LOCK_DIR, self.config.LOCK_FILE, self.logger)

		##debug output
		self.logger.debug('Crontab Initial')
		self.logger.debug('[SERVICE_INTERVAL][%s]' % (self.config.SERVICE_INTERVAL))
		self.logger.debug('[CRONTAB_CFG_DIR][%s]' % (self.config.CRONTAB_CFG_DIR))
		self.logger.debug('[CRONTAB_CFG_FILE][%s]' % (self.config.CRONTAB_CFG_FILE))
		self.logger.debug('[MAX_THREADS][%s]' % (self.config.MAX_THREADS))
		self.logger.debug('[THREAD_TIMEOUT][%s]' % (self.config.THREAD_TIMEOUT))
		self.logger.debug('[LOCK_DIR][%s]' % (self.config.LOCK_DIR))
		self.logger.debug('[LOCK_FILE][%s]' % (self.config.LOCK_FILE))
		self.logger.debug('[LOG_DIR][%s]' % (self.config.LOG_DIR))
		self.logger.debug('[LOG_FILE][%s]' % (self.config.LOG_FILE))
		self.logger.debug('[LOG_LEVEL][%s]' % (self.config.LOG_LEVEL))
		self.logger.debug('[LOG_MAX_SIZE][%s]' %(self.config.LOG_MAX_SIZE))
		self.logger.debug('[LOG_BACKUP_COUNT][%s]' %(self.config.LOG_BACKUP_COUNT))

		##crontab initial
		#self.crontabObj = Crontab(self.config.CRONTAB_CFG_FILE, self.logger, self.config.MAX_THREADS, self.config.THREAD_TIMEOUT)

		return(None)

	##initial logger
	def logger_init(self):

		self.logger = logging.getLogger("SACheck")

		try:
			log_level = getattr(logging, self.config.LOG_LEVEL)
		except:
			log_level = logging.NOTSET

		self.logger.setLevel(log_level)

		fh = RotatingFileHandler(self.config.LOG_FILE, mode='a', maxBytes=self.config.LOG_MAX_SIZE, backupCount=self.config.LOG_BACKUP_COUNT)
		fh.setLevel(log_level)

		ch = logging.StreamHandler()
		ch.setLevel(log_level)

		formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s')
		fh.setFormatter(formatter)
		ch.setFormatter(formatter)

		self.logger.addHandler(fh)
		self.logger.addHandler(ch)

		return(True)

	##run crontab function
	def run(self):

		while True:

			##crontab initial
			self.crontabObj = Crontab(self.config.CRONTAB_CFG_FILE, self.logger, self.config.MAX_THREADS, self.config.THREAD_TIMEOUT, self.config.SUBPROC_LIMITS, self.config.MAX_RETRY, self.config.THREAD_DELAY)
			self.crontabObj.run()
			time.sleep(self.config.SERVICE_INTERVAL)

		return(True)

	##destructor function
	def __del__(self):

		##lock release
		try:
			self.lockObj.lock_release(self.config.LOCK_FILE)
		except Exception, e:
			pass

		return(None)

##New CrontabServiceObj
crontabServiceObj = CrontabService()
crontabServiceObj.run()

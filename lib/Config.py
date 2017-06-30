'''
    Config module
    Read Configs From etc/global.conf
    Written By Kyle Chen
    Version 20170628v1
'''

##import buildin pkgs
import os
import re
import sys
import ConfigParser

##Config Class
class Config:

    ##initial function
    def __init__(self, workpath):

	##get workpath
	self.workpath = workpath

	##set config file point
        global_filepath = '%s/etc/global.conf' % (self.workpath)
        configParserObj = ConfigParser.ConfigParser()
        configParserObj.readfp(open(global_filepath, 'rb'))

	##initial config vars
        self.SERVICE_INTERVAL = int(configParserObj.get('service', 'SERVICE_INTERVAL'))

        self.CRONTAB_CFG_DIR = configParserObj.get('crontab', 'CRONTAB_CFG_DIR')
	self.CRONTAB_CFG_DIR = '%s/%s' % (self.workpath, self.CRONTAB_CFG_DIR)
        self.CRONTAB_CFG_FILE = configParserObj.get('crontab', 'CRONTAB_CFG_FILE')
	self.CRONTAB_CFG_FILE = '%s/%s' % (self.CRONTAB_CFG_DIR, self.CRONTAB_CFG_FILE)

        self.MAX_THREADS = int(configParserObj.get('thread', 'MAX_THREADS'))
        self.THREAD_TIMEOUT = int(configParserObj.get('thread', 'THREAD_TIMEOUT'))
        self.SUBPROC_LIMITS = int(configParserObj.get('thread', 'SUBPROC_LIMITS'))
        self.MAX_RETRY = int(configParserObj.get('thread', 'MAX_RETRY'))
        self.THREAD_DELAY = int(configParserObj.get('thread', 'THREAD_DELAY'))

        self.LOCK_DIR = configParserObj.get('lock', 'LOCK_DIR')
	self.LOCK_DIR = '%s/%s' % (self.workpath, self.LOCK_DIR)
        self.LOCK_FILE = configParserObj.get('lock', 'LOCK_FILE')
	self.LOCK_FILE = '%s/%s' % (self.LOCK_DIR, self.LOCK_FILE)

        self.LOG_DIR = configParserObj.get('log', 'LOG_DIR')
	self.LOG_DIR = '%s/%s' % (self.workpath, self.LOG_DIR)
        self.LOG_FILE = configParserObj.get('log', 'LOG_FILE')
	self.LOG_FILE = '%s/%s' % (self.LOG_DIR, self.LOG_FILE)
        self.LOG_LEVEL = configParserObj.get('log', 'LOG_LEVEL').upper()
        self.LOG_MAX_SIZE = int(configParserObj.get('log', 'LOG_MAX_SIZE')) * 1024 * 1024
        self.LOG_BACKUP_COUNT = int(configParserObj.get('log', 'LOG_BACKUP_COUNT'))

	self.dir_init(self.LOCK_DIR)
	self.dir_init(self.LOG_DIR)

	return(None)

    ##directory initial function
    def dir_init(self, dir):

        if not os.path.exists(dir):

	    try:

		os.mkdir(dir)

	    except Except, e:

		sys.stderr.write('[Error][%s]' % ( e ))
		sys.stderr.flush()

	return(True)

    ##destructor function
    def __del__(self):

	return(None)

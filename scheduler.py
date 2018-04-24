# -*- coding: utf-8 -*-
'''
Created on 2012-4-18

@author: vertusd
'''

from apscheduler.scheduler import Scheduler
import logging,sys
from celery.task.sets import TaskSet
from celery import chain
import tasks
from celery.decorators import task
from sqlalchemy.orm import sessionmaker
from models import *
from sqlalchemy import create_engine
from taskMeta import *
import datetime
from taskMaker import *
import sys, time
from daemon import Daemon

class ScheduleManager(object):
    '''
    classdocs
    '''
    
    m_instance=None
    taskMakingJobs= []

    def __init__(self):
        '''
        Constructor
        '''
        self.scheduler =Scheduler()
        self.scheduler.start()
        
        
    @classmethod
    def getInstance(cls):
        if cls.m_instance is None:
            cls.m_instance = cls()
        return cls.m_instance

    def stopAll(self):
        #unschedule all jobs
        for job in self.scheduler.get_jobs():
            self.scheduler.unschedule_job(job)
        

    def startMakingTaskSch(self):
        logging.debug('start maketask schedule func running:')
        if self.taskMakingJobs:
            for job in self.taskMakingJobs:
                if job in self.scheduler.get_jobs():
                    print "unscribe schedule"
                    self.scheduler.unschedule_job(job)
            del self.taskMakingJobs[:]
            self.taskMakingJobs=[]
            
        makeTasks()
        retryLimit=5
        attempt=0
        scrapeInterval = getCronTime()
        print u"启动抓取计划任务 after: " + unicode(scrapeInterval)
        logging.debug("start make task after : %d" % scrapeInterval)
        while not self.taskMakingJobs and attempt<retryLimit:
            try:
                self.taskMakingJobs.append(self.scheduler.add_interval_job(ScheduleManager.getInstance().startMakingTaskSch, seconds =scrapeInterval))
            except:
                logging.debug('exception at adding scrapejob:')
                logging.debug(sys.exc_info())
            attempt+=1
        if attempt >1:
            logging.debug('attempt %d times to add scrapejob:'%(attempt))
        logging.debug('end schedule scrape func running:')



    def makeTask(self):
        #抓取前先发送当前状态
        logging.debug('end add scrape tasks:')




class MyDaemon(Daemon):
    def run(self):
        print "starting scheduler... "
        logging.basicConfig(filename = os.path.join(, 'fetiupdater.log'), level = logging.DEBUG)
        logging.debug("starting scheduler...")
        schedule = ScheduleManager()
        #schedule.daemonic = False  
        schedule.startMakingTaskSch()
        while True:
            time.sleep(20)
 
if __name__ == "__main__":
        daemon = MyDaemon('/tmp/fetidaemon.pid')
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        daemon.restart()
                else:
                        print "Unknown command"
                        sys.exit(2)
                #sys.exit(0)
        else:
                print "usage: %s start|stop|restart" % sys.argv[0]
                sys.exit(2)
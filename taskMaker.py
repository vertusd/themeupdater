from sqlalchemy.sql import text
from celery import chain
import tasks
from celery.decorators import task
from sqlalchemy.orm import sessionmaker
from theme_models import *
from sqlalchemy import create_engine
from taskMeta import *
import datetime
import time
from celery import Celery






def calcTimeSeconds(p_timestr):
        try:
            l_time = time.strptime(p_timestr,"%H:%M:%S")
        except:
            return -1
        l_timecount = l_time.tm_hour * 60 * 60
        l_timecount += l_time.tm_min * 60
        l_timecount += l_time.tm_sec
        return int(l_timecount)

def getCronTime():
    engine = create_engine('mysql://my_db_user:Appuser@01@127.0.0.1:3306/envto_db?charset=utf8', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    schedule = session.query(Schedule).filter_by(id=1).first()
    print "products per day : " + str(schedule.product_perday)
    l_curtime = calcTimeSeconds(datetime.datetime.now().__str__()[11:19])

    return int(l_curtime/schedule.movies_perday)


def makeDownloadTask(product):
    print "Make Product Download Task :" + str(product.id)
    taskMeta = TaskMeta(product.id, State.DOWNLOADING, None)
    return tasks.download_task.s(product.sample_url, "/home/vertusd/job_downloads/", taskMeta)

def makeCompressTask():
    return tasks.compress_task.s()

def makeUploadTask():
    return tasks.upload_task.s()

def makeUpdateDBTask():
    return tasks.update_database.s()

def makeUpdateBlogTask():
    return tasks.update_blog.s()


def makeTasks():
    #logging.debug("starting making tasks" )
    app = Celery()
    app.config_from_object('celeryconfig')
    engine = create_engine('mysql://my_db_user:Appuser@01@127.0.0.1:3306/envto_db?charset=utf8', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    schedule = session.query(Product).filter_by(id=1).first()
    """
    product = session.query(Product.categories,Product.sample_url,Product.url,Product.id)\
        .filter(Product.uploaded==False)\
        .order_by(Product.priority_score).first()
    """


    for product in session.query(Product)\
                          .from_statement(text("select p.* from products as p ,categories as c, product_cat as pc \
                                                where p.uploaded =0 and pc.product_id = p.id and pc.category_id = c.id \
                                                and c.name like :categorie_name \
                                                order by p.priority_score desc \
                                                limit :result_start,:result_limit;"))\
                          .params(categorie_name='after-effects-project-files%',result_limit=100,result_start=104)\
                          .all():
        chain(makeDownloadTask(product), makeUploadTask(), makeUpdateDBTask()).apply_async()
        time.sleep(60*8)
    return

def makeTasksOld():

    taskchain = chain(makeDownloadTask(), makeCompressTask(), makeUploadTask(), makeUpdateDBTask(), makeUpdateBlogTask()).apply_async()
    print "Sending tasks"
    results = list(taskchain.collect())
    print "Waiting for results"
    #results = taskchain.get()
    return

if __name__ == "__main__":
    makeTasks()

import os,sys
from celery import current_task
import subprocess
from sqlalchemy.orm import sessionmaker
from theme_models import *
from sqlalchemy import create_engine
from taskMeta import *
import traceback
import xmlrpclib
username = 'Admin'
password = 'Appuser@01'
from celery import Celery
import yapi
import ast
import sys
import json
import re
import regex
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





app = Celery()
app.config_from_object('celeryconfig')


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


def cleanhtml(raw_html):
  cleanr = re.compile(u'<.*?>')
  cleantext = re.sub(cleanr, u'', raw_html)
  return cleantext

def add_ref(url):
    if url.find(u"?ref=") > 0:
        return url.split("?ref=")[0]+ "?ref=milestance" 
    if url.find(u"&ref=") > 0:
        return url.split("&ref=")[0] + "&ref=milestance" 
    if url.find(u"?") > 0:
        return  url + "&ref=milestance" 
    else:
        return url + "?ref=milestance" 

def buildProductInfo(product):
    #productInfo={title:"", desc:"", cat:""}
    arg = u"youtube-upload"
    music_match = re.findall(r'\"(http\w*?://audiojungle\.net/.+?)(?:ref=|\"|\s)', product.info.description_html)
    if music_match:
        new_music_match = [add_ref(match) for match in music_match if match.find("audiojungle") >0]
        music_desc = "Download music: \n" + u"\n".join(new_music_match)
    else:
        music_desc = u""

    de_match = re.search(r"item-description_.+?>(.*)(?:<h2|eatures|item-description\w*)?", product.info.description_html, re.DOTALL | re.MULTILINE)
    if de_match:
        de_desc = "Description: \n" + de_match.group(1)
        if (de_desc.find("http") > 0):
            de_desc = u""
    else:
        print "no match for description__des, using full html "
        de_desc = u""
    
    fe_match = re.search("item-description_.*?_features.+?<li>(.*)</li>.+?item-description\w*?", product.info.description_html, re.DOTALL | re.MULTILINE)
    if fe_match:
        fe_desc = fe_match.group(1)
    else:
        print "no match for description__features, using full html "
        fe_desc = product.info.description_html
    fe_match = re.findall(r"<li>(.+?)</li>", fe_desc,  re.DOTALL |re.MULTILINE)
    if fe_match:
        new_fe_match = [li.strip() for li in fe_match if li.find("href")<=0 and li.find("img") <=0 and len(li) >2]
        fe_desc = u"Features:\n" +u"\n".join(new_fe_match)
    else:
        print "no match for fe_match"
        fe_desc = u""

    try: 
        description =cleanhtml(u"""Download template:\n%s \n%s\n\n%s\n%s \n\nThemeLight After Effects Templates channel chose the latest and best templates for Adobe After Effect from Videohive Envato Marketplace. ThemeLight After Effects Templates channel provide the most popular templates as Slideshow, Opener, Logo, Reel, Showreel, Demo reel, Intro, Broadcast packages, Elements packages, Lower Third, Titles, Typography and other the best of animations templates for your pleasure, holidays and business."""\
                      % (add_ref(product.url), music_desc,de_desc, fe_desc))
        arg += u" --title=\"%s\"" % (product.title.strip() + u" | After Effects Template")
        arg += u" --description=\"%s\"" %(description)
        arg += u" --category=\"%s\"" %(u"Film & Animation")
        arg += u" --tags=\"%s\"" %(' '.join([str(tag).strip() for tag in product.tags]))
        arg += u" --client-secrets=%s" %("/home/vertusd/themeUpdater/client.json")
        arg += u" --playlist=%s" %(unicode(product.categories[0]).replace(u"after-effects-project-files/",u"").replace(u"/",u"_").strip())


    except:
        print sys.exc_info()
        import traceback
        print traceback.print_exc()
        print "fail to parse:" + str(product.id) + "\n"
        
    return arg
@app.task
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
                          .params(categorie_name='after-effects-project-files%',result_limit=1,result_start=104)\
                          .all():
        chain(makeDownloadTask(product), makeUploadTask(), makeUpdateDBTask()).apply_async()
    return

@app.task
def download_task(url, savePath, taskMeta=None):
    try:
        import urllib2
        file_name = url.split('/')[-1]
        u = urllib2.urlopen(url)
        header = u.info().getheader('Content-Length')

        file_size = int(header.strip())
        if os.path.exists(os.path.join(savePath, file_name)) and int(os.stat(os.path.join(savePath, file_name)).st_size) == file_size:
            print "file exists and downloaded: " + file_name
            return [os.path.join(savePath, file_name),taskMeta]
        f = open(os.path.join(savePath, file_name), 'wb')
        print "Downloading: %s Bytes: %s" % (file_name, file_size)
        file_size_dl = 0
        block_sz = 81920
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            current_task.update_state(state='PROGRESS',
                meta={'current': int(file_size_dl * 100 / file_size) , 'total': 100})
            file_size_dl += len(buffer)
            
            f.write(buffer)
        f.close()
    except:
        traceback.print_exc()
        taskMeta.state = State.DOWNLOADFAILED
    taskMeta.state = State.DOWNLOADED
    return [os.path.join(savePath, file_name),taskMeta]

@app.task
def upload_task(params):
    taskMeta = params[1]
    upload_result =False
    try:
        engine =  create_engine('mysql://my_db_user:Appuser@01@127.0.0.1:3306/envto_db?charset=utf8', echo=False)
        Session = sessionmaker(bind=engine)
        session =  Session()
        product = session.query(Product).filter_by(id=taskMeta.productId).first()
        arg = ""
        srcPath = params[0]
        srcFileName = srcPath.split("/")[-1]
        if product:
            if product.uploaded == True:
                print "product is uploaded. aboart!!"
                return [upload_result, taskMeta]
            arg = buildProductInfo(product) + u" " + unicode(srcPath)

        taskMeta = params[1]
        os.chdir("/home/vertusd/")
        print u"arg:" + arg 
        results = os.popen(arg.encode("utf-8")).readlines()
        print u"results is :\n" 
        for line in results:
            print line
        print "len: " + str(len(results[-1]))
        if (results[-1].find(u"error") <0 and len(results[-1]) > 10 and  len(results[-1]) < 14 and results[-1].find(u" ") <=0):
            upload_result = True
    except:
        traceback.print_exc()
        taskMeta.state = State.UPLOADFAILED
    session.close()
    taskMeta.state = State.UPLOADED
    return [upload_result, taskMeta]
@app.task
def update_database(params):
    upload_result = params[0]
    taskMeta = params[1]
    productId =taskMeta.productId
    engine =  create_engine('mysql://my_db_user:Appuser@01@127.0.0.1:3306/envto_db?charset=utf8', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    product = session.query(Product).filter_by(id=taskMeta.productId).first()
    if not product:
        taskMeta.error = "No Product Founded by ID: " + productId
        taskMeta.state = State.up.UPDATEDBFAILED
        return [productId, taskMeta]
    product.uploaded = upload_result
    session.add(product)
    session.commit()
    taskMeta.state = State.FINISHED
    return [productId, taskMeta]
"""
@app.task
def compress_task(params):
    srcPath = params[0]
    srcFileName = srcPath.split("/")[-1]
    taskMeta = params[1]


    try:

        args = []
        os.chdir("/home/vertusd/")
        arg = 'ffmpeg -y -i %s -acodec copy -vcodec msmpeg4 -qscale 2  -vf "movie=/home/vertusd/video/topfetish.png [watermark]; [in][watermark] overlay=20:main_h-overlay_h [out]" %s_output.wmv' % (srcFileName, srcFileName)
        print os.popen(arg).readlines()
    except:
        traceback.print_exc()
        taskMeta.state = State.CONVERTFAILED
    taskMeta.state = State.CONVERTED
    taskMeta.compressUrl = srcFileName + "_output.wmv"
    taskMeta.fileUrl = srcPath
    return [srcPath.replace(srcFileName, srcFileName + "_output.wmv"), taskMeta]
"""


"""
@app.task
def upload_task(params):
    taskMeta = params[1]
    try:
        srcPath = params[0]
        srcFileName = srcPath.split("/")[-1]
        taskMeta = params[1]
        os.chdir("/home/vertusd/")
        arg = "plowup --auth=topfetish@outlook.com:2TkWlP rapidgator " + srcFileName
        results = os.popen(arg).readlines()
        print results[-1]
    except:
        traceback.print_exc()
        taskMeta.state = State.UPLOADFAILED


    taskMeta.state = State.UPLOADED
    return [results[-1], taskMeta]

@app.task
def update_database(params):
    httpPath = params[0]
    srcFileName = httpPath.split("/")[-1]
    taskMeta = params[1]
    movieId =taskMeta.movieId
    engine = create_engine('mysql://feti:feti123456@192.64.114.146:3306/feti?charset=utf8', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    movie = session.query(Movie).filter_by(id=movieId).first()
    if not movie:
        taskMeta.error = "No Movie Founded by ID: " + movieId
        taskMeta.state = State.UPDATEDBFAILED
    movie.state = State.UPDATEDDB
    remoteUrl = RemoteUrl(httpPath)
    remoteUrl.movie = movie
    session.add(remoteUrl)
    #session.update(movie)
    session.commit()
    return [movieId, taskMeta]
"""
@app.task
def update_blog(params):
    movieId = params[0]
    taskMeta = params[1]
    engine = create_engine('mysql://feti:feti123456@192.64.114.146:3306/feti?charset=utf8', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    movie = session.query(Movie).filter_by(id=movieId).first()
    host = xmlrpclib.ServerProxy('http://top-fetish.com/xmlrpc.php')
    custom_field = movie.thumb_images[0].url
    blog_id = 0
    title = movie.title
    content = movie.description
    tagString = u""
    for tag in movie.tags:
        tagString += (u"%s," % ( tag.name))
    cats= []
    for cat in movie.categories:
        cats.append(cat.name)

    remoteUrl = movie.remote_url[0]
    content += u"<p><a href='%s'>%s</a></p></br><p><div id='desc_div'>" % (remoteUrl.url, remoteUrl.url)
    for img in movie.desc_images:
        #print "image" + img.url
        imageStr = u"<img src='%s'></img>" % (img.url)
        #print imageStr
        content += imageStr
    content += u"</div></br><div><a href='http://rapidgator.net/article/premium/ref/1434669' target='_blank'><img src='http://rapidgator.net/images/banners/690_468x80.gif' border='0' width='468' height='80' alt='Rapidgator.net'/></a></div></p>"
    entry = { 'post_title' : title, 'post_content' : content, 'post_tags' : tagString, 'post_category' : cats }
    entry_id =host.wp.pythonAddPost(blog_id, username, password, entry, custom_field)
    host.mt.publishPost(entry_id, username, password)
    taskMeta.state = State.FINISHED
    movie.state = State.FINISHED
    schedule = session.query(Schedule).filter_by(id=1).first()
    schedule.last_movie_id = movieId
    session.commit()
    print "remove :" + taskMeta.compressUrl
    print "remove :" + taskMeta.fileUrl
    os.remove(taskMeta.compressUrl)
    os.remove(taskMeta.fileUrl)
    return True


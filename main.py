#coding=utf-8
from scrapy.item import Item, Field
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.spider import BaseSpider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy.crawler import CrawlerProcess
from scrapy.http.response.html import HtmlResponse
from urllib2 import urlopen
import urllib
import cookielib
import urllib2
import re
import sqlite3
import sys
from sqlalchemy.orm import sessionmaker
from models import *
from sqlalchemy import create_engine

def login(user,password):
    result = u""
    url = "http://www.feti072.com/login.php"
    cj =None
    try:
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent':user_agent,} 
        cj = cookielib.CookieJar()
        data = {'uid':user.encode('sjis'), 'pwd':password.encode('sjis') , "submit_flg":u"ログイン".encode('sjis')}
        data = urllib.urlencode(data)  
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        request = urllib2.Request(url,None,headers) 
        result = opener.open(request, data ,timeout=120)
        html = result.read()
        if result:
            webdata =  HtmlResponse(url,body=html)
        else:
            webdata = HtmlResponse(url,body="")
    except:
        print "fail to fetch:" + url
        print sys.exc_info()
        import traceback
        print traceback.print_exc()
        print result
        return None
    
    if webdata.body_as_unicode().find(u"ログアウト") > 0:
        print "login successfully"
        return cj

def getResponse(id,cookieJar): 
    result = u""
    s = "%20"
    url = u"""http://www.feti072.com/g0/%s.html""" % (id)
    #print "startDownloading " ,url
    try:
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent':user_agent,}
        if cookieJar:
            cj = cookieJar
        else:
            cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        request = urllib2.Request(url,None,headers) 
        result =opener.open(request,timeout=120)
        html = result.read()
        if result:
            webdata =  HtmlResponse(url,body=html)
        else:
            webdata = HtmlResponse(url,body="")
        #print "endDownloading " ,url
    except:
        print "fail to fetch:" + url
        print sys.exc_info()
        import traceback
        print traceback.print_exc()
        print result
        return HtmlResponse(url, body=u"null".encode("utf-8"))
    return webdata

def parseRespones(result, rawId, engine):
    if result.body_as_unicode().find(u"Something is wrong in your syntax") > 0:
        print "not exsist id"

    #newresponse = HtmlResponse(url=response.url,body=response.body_as_unicode().encode('utf-8'))
        
    hxs = HtmlXPathSelector(result)
    smpString =u'//div[@class="dl"]//a[contains(img/@src,"btn_dl_smp_0")]/@href'
    lowString =u'//div[@class="dl"]//a[contains(img/@src,"btn_dl_0_0")]/@href'
    midString =u'//div[@class="dl"]//a[contains(img/@src,"btn_dl_10_0")]/@href'
    highString =u'//div[@class="dl"]//a[contains(img/@src,"btn_dl_20_0")]/@href'
    titleString = u'//div[@class="title-h-l"]/h1/text()'
    categoryString = u'//div[@class="title-category"]//a'
    tagsString = u'//div[@class="title-keyword"]//a'
    descriptionsString = u'//div[@class="title-description"]//text()'
    thumbsString = u'//div[@class="titledetail-stillpic"]//img'
    thumbsString2 = u'//div[@class="titledetail-pic"]//img'
    
    descImagesString = u'//div[@class="titledetail-cap"]//img'

    smpVideo =  hxs.select(smpString).extract()
    lowVideo =  hxs.select(lowString).extract()
    midVideo =  hxs.select(midString).extract()
    highideo =  hxs.select(highString).extract()
    title = hxs.select(titleString).extract()
    categories = hxs.select(categoryString)
    tags = hxs.select(tagsString)
    descriptions = hxs.select(descriptionsString).extract()
    thumbs = hxs.select(thumbsString)
    thumbs.extend(hxs.select(thumbsString2))
    descImages = hxs.select(descImagesString)

    smpUrl = smpVideo[0].encode("utf-8") if smpVideo else ""
    lowUrl = lowVideo[0].encode("utf-8") if lowVideo else ""
    midUrl = midVideo[0].encode("utf-8") if midVideo else ""
    highUrl =  highideo[0].encode("utf-8") if highideo else ""

    tagObjs = []
    categoryObjs = []
    thumbObjs = []
    descImageObjs = []
    Session = sessionmaker(bind=engine)
    session = Session()

    if session.query(Movie).filter_by(raw_id=rawId).first():
        print "Movie of raw id %d already saved" % (rawId)
        return
    if tags:
        for tag in tags:
            tagUrl = tag.select('./@href').extract()[0]
            tagName  = tag.select(".//text()").extract()[0]
            tagObj = session.query(Tag).filter_by(name=tagName).first()
            if not tagObj:
                tagObj = Tag(tagUrl, tagName)
                session.add(tagObj)
                tagObjs.append(tagObj)
            

            
    if categories:
        for cat in categories:
            catUrl = cat.select('./@href').extract()[0]
            catName = cat.select('.//text()').extract()[0]
            catObj = session.query(Category).filter_by(name=catName).first()
            if not catObj:
                catObj = Category(catUrl, catName)
                categoryObjs.append(catObj)
                session.add(catObj)
                #print u"save" + catObj.__repr__()
            
       
    if thumbs:
        for thumb in thumbs:
            thumbUrl = thumb.select('./@src').extract()[0]
            thumbObj = ThumbImage(thumbUrl)
            thumbObjs.append(thumbObj)
            session.add(thumbObj)
            #print u"save" + thumbObj.__repr__()


    if descImages:
        for image in descImages:
            imageUrl = image.select('./@src').extract()[0]
            descImagesObj = DescImage(imageUrl)
            descImageObjs.append(descImagesObj)
            session.add(descImagesObj)
            #print u"save" + descImagesObj.__repr__()

    if title:
        title = title[0]
    else:
        title = "no title"
    if descriptions:
        description = "".join(descriptions)
    else:
        description = "no description"

    movie = Movie(rawId, title, description, highUrl, midUrl, lowUrl, smpUrl)
    
    for cat in categoryObjs:
        movie.categories.append(cat) 
    for tag in tagObjs:
        movie.tags.append(tag)
    
    for descImage in descImageObjs:
        movie.desc_images.append(descImage)
    for thumb in thumbObjs:
        movie.thumb_images.append(thumb)

    session.add(movie)
    session.commit()
    print "saved movie" + str(rawId)

    return 

def saveToDatabase(parsedResults,con):
    if len(parsedResults) != 6:
        print "empty results"
        return

    cur = con.cursor()
    cmd = u"""INSERT INTO user (userid,name,email,password,key,status) values ("%s", "%s","%s","%s","%s","%s");  """ % (parsedResults[0], parsedResults[1],parsedResults[2].replace(u"[退会]",""),parsedResults[3],parsedResults[4],parsedResults[5])
    #print cmd
    cur.execute(cmd)

    con.commit()


def startExtract(cookie):
    i = 1332
    engine = create_engine('mysql://feti:feti123456@192.64.114.146:3306/feti?charset=utf8', echo=False)
    while i < 2108:
        print "start download"
        result = getResponse(i,cookie)
        print "end downlaod"
        try:
            
            parsedResult = parseRespones(result,i,engine)
            #print parsedResult.encode("utf-8")
            #saveToDatabase(parsedResult,con)
        except:
            print sys.exc_info()
            import traceback
            print traceback.print_exc()
            print "error on : " + str(i)
        i += 1
        import time
        time.sleep(2)

if __name__ == "__main__":
    #print '\xb7\xa2\xc9\xfa\xd2\xe2\xcd\xe2\xa1\xa3'.encode("GBK")
    cookie = login(u"kamemasu1234",u"88881111")
    print cookie
    if cookie:
        startExtract(cookie)
    else:
        print "login failed!"


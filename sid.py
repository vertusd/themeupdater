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


def parseRespones(result, rawId):
    if result.body_as_unicode().find(u"Something is wrong in your syntax") > 0:
        print "not exsist id"

    #newresponse = HtmlResponse(url=response.url,body=response.body_as_unicode().encode('utf-8'))
        
    hxs = HtmlXPathSelector(result)
    lowString =u'//div[@class="dl"]//a[contains(img/@src,"btn_dl_0_0")]/@href'
    lowVideo =  hxs.select(lowString).extract()
    lowUrl = lowVideo[0].encode("utf-8") if lowVideo else ""

    return  lowUrl.split("/") [-2]


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



def getSid():
    cookie = login(u"kamemasu1234",u"88881111")
    result = getResponse(1332,cookie)
    return parseRespones(result,1332)

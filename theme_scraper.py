#coding=utf-8

from urllib2 import urlopen
import urllib
import cookielib
import urllib2
import re
import sqlite3
import sys
import json
from sqlalchemy.orm import sessionmaker
from theme_models import *
from sqlalchemy import create_engine
import requests
from dateutil import parser,tz
from datetime import datetime
import pickle
import yappi

global GLOBE_COOKIE
GLOBE_COOKIE = cookielib.LWPCookieJar()
sys.setrecursionlimit(1000)
max_scale=5800
final_filter_list=[]
class IntegerFilter(object):
    range_min=0
    range_max=100000
    scale=1
    is_range=True
    def  __init__(self, range_min, range_max, scale, is_range=True):
        self.range_min = range_min
        self.range_max = range_max
        self.scale = scale
        self.is_range= is_range
    def __unicode__(self):
        return unicode((self.range_min, self.range_max))

    def __str__(self):
        return str((self.range_min, self.range_max))

    def __repr__(self):
        return str((self.range_min, self.range_max))

class VideoDurationFileter(object):
    range_min=0
    range_max=86400
    #seconds
    scale=1
    def  __init__(self, range_min, range_max, scale):
        self.range_min = range_min
        self.range_max = range_max
        self.scale = scale
    def __unicode__(self):
        return unicode((self.range_min, self.range_max))

    def __str__(self):
        return str((self.range_min, self.range_max))

    def __repr__(self):
        return str((self.range_min, self.range_max))

def split_filter(filter_combine):
    for idx in range(0, len(filter_combine)):
        if filter_combine[idx].is_range == False:
            result_filter_list = []
            if filter_combine[idx].range_max == filter_combine[idx].range_min:
                continue
            for f_idx in range(0, filter_combine[idx].range_max+1):
                result_combine=filter_combine[:]
                result_combine[idx]=IntegerFilter(f_idx, f_idx , filter_combine[idx].scale,False)
                result_filter_list.append(result_combine)
            print "split:" + str(filter_combine) + "toDiv:" + str(0) + " to " + str(filter_combine[idx].range_max)
            return (True,result_filter_list)
        else:
            if (filter_combine[idx].range_max-filter_combine[idx].range_min) > filter_combine[idx].scale-1:
                mid_range = (filter_combine[idx].range_max+filter_combine[idx].range_min)/2
                low_filter = IntegerFilter(filter_combine[idx].range_min, mid_range , filter_combine[idx].scale)
                high_filter = IntegerFilter(mid_range +1,filter_combine[idx].range_max, filter_combine[idx].scale)
                low_filter_combine=filter_combine[:]
                low_filter_combine[idx]=low_filter
                high_filter_combine=filter_combine[:]
                high_filter_combine[idx]=high_filter
                print "split:" + str(filter_combine) + "to:" + str(low_filter_combine) + "-" + str(high_filter_combine)
                result_filter_list = []
                result_filter_list.append(low_filter_combine)
                result_filter_list.append(high_filter_combine)
                return (True,result_filter_list)
    return (False,[filter_combine])



def divide(filter_combine, site_name):
    s_result = json.loads(getResponse(filter_combine, 1, site_name))
    print "search result :" + str(s_result["total_hits"]) 
    if int(s_result["total_hits"]) ==0:
        print "s_result is zero :- filter:" + str(filter_combine)
        return
    if int(s_result["total_hits"]) > max_scale:
        split_result = split_filter(filter_combine)
        if split_result[0] == True:
            #low_data_set = getResponse(split_result[1], 100, site_name)
            #high_data_set = getResponse(split_result[2], 100, site_name)
            for result in split_result[1]:
                divide(result, site_name)
        
        else:
            print "fail to split:" + str(split_result[1])
            print "add to final_filter_list"
            import sys
            sys.exit(-1)
            #final_filter_list.append(filter_combine)

    else:
        final_filter_list.append(filter_combine)

def num_to_time(num):
    return str(num/60) + ":" + str(num%60).zfill(2)

def getResponse(filter_range_combine, page, site_name): 
    webdata = u""
    frames_list=["23.98","24", "25", "29.97", "30", "48", "50", "59.94", "60"]
    sale_list = ["rank-0","rank-1","rank-2","rank-3","rank-4",]
    rate_list = ["1", "2", "3", "4"]
    price_min = filter_range_combine[0].range_min
    price_max = filter_range_combine[0].range_max
    #time_min = num_to_time(filter_range_combine[1].range_min)
    #time_max = num_to_time(filter_range_combine[1].range_max)
    #frames_min = filter_range_combine[1].range_min
    #frames_max = filter_range_combine[1].range_max
    sales_min = filter_range_combine[1].range_min
    sales_max = filter_range_combine[1].range_max
    rate_min = filter_range_combine[2].range_min
    rate_max = filter_range_combine[2].range_max

    url = u"https://api.envato.com/v1/discovery/search/search/item?category=after-effects-project-files&site=%s&price_max=%s&price_min=%s&page=%s&page_size=100" % (site_name,price_max, price_min, page)
    #print "startDownloading " ,url
    """
    if frames_min == frames_max:
        url = url + "&frame_rate=" + frames_list[frames_min]
    """
    if sales_min == sales_max:
        url = url + "&sales=" + sale_list[sales_min]
    if rate_max == rate_min:
        url = url + "&rating_min=" + rate_list[rate_max]
    print u"fetch url: " + url
    try:
        headers = {"Authorization":"Bearer NdlBDRUM651s8hhWEQlsUNqPbzC4omhi"}
        #urllib2.install_opener(proxy_opener)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(GLOBE_COOKIE))
        request = urllib2.Request(url,None,headers) 
        result = opener.open(request ,timeout=120)
        webdata = result.read()
        #print "endDownloading " ,url
    except:
        print "fail to fetch:" + url
        print sys.exc_info()
        import traceback
        print traceback.print_exc()
        print webdata
        return webdata
    return webdata

def checkFilters(site_name):
    int_filter = IntegerFilter(0, 100000, 1)
    vid_filter = IntegerFilter(0, 86400, 1)
    #int_filter = IntegerFilter(0, 8, 1)
    #vid_filter = IntegerFilter(0, 100, 1)
    #frames_filter = IntegerFilter(0, 8, 1, False)
    rate_filter = IntegerFilter(0, 3, 1, False)
    sales_filter = IntegerFilter(0, 4, 1, False)
    filter_list= [int_filter, sales_filter, rate_filter]
    divide(filter_list, site_name)



def getUserResponse(page):
    webdata = u""
    url = u"https://forums.envato.com/directory_items?asc=true&order=likes_received&page=%d&period=all&_=1502282844193" % page
    #print "startDownloading " ,url
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"\
                   , "X-Requested-With": "XMLHttpRequest"}
        #urllib2.install_opener(proxy_opener)
        #proxy = urllib2.ProxyHandler({'http': '127.0.0.1:1080'})
        #proxy_opener = urllib2.build_opener(proxy)
        #urllib2.install_opener(proxy_opener)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(GLOBE_COOKIE))
        request = urllib2.Request(url,None,headers) 
        result = opener.open(request ,timeout=120)
        webdata = result.read()
        #print "endDownloading " ,url
    except:
        print "fail to fetch:" + url
        print sys.exc_info()
        import traceback
        print traceback.print_exc()
        print webdata
        return webdata
    return webdata


def getUserBadges(username):
    webdata = u""
    url = u"https://api.envato.com/v1/market/user-badges:%s.json" % username
    #print "startDownloading " ,url
    try:
        headers = {"Authorization":"Bearer NdlBDRUM651s8hhWEQlsUNqPbzC4omhi"}
        #urllib2.install_opener(proxy_opener)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(GLOBE_COOKIE))
        request = urllib2.Request(url,None,headers) 
        result = opener.open(request ,timeout=120)
        webdata = result.read()
        #print "endDownloading " ,url
    except:
        print "fail to fetch:" + url
        print sys.exc_info()
        import traceback
        print traceback.print_exc()
        print webdata
        return webdata
    return webdata


#获取价格范围的结果
def getRangeResponse(filter_range_combine, site_name):
    page =1 
    
    while True:
        print "fetch page : %d" % page
        jsonObj = json.loads(getResponse(filter_range_combine, page, site_name))
        if len(jsonObj["matches"]) == 0:
            return
        yield jsonObj
        if jsonObj["links"]["next_page_url"]  is None:
            return 
        page+=1
      
#获取价格范围结果并保存
def getFilterRange(filter_range_combine, site_name, session):
    result = False
    for jsonObj in getRangeResponse(filter_range_combine, site_name):
        print "size :%d" % len(jsonObj["matches"])
        for match in  jsonObj["matches"]:
            from time import clock
            start=clock()
            saveRespones(match, site_name, session)
            finish=clock()
            print "save time:" + str((finish-start))

#获取用户列表的结果
def getAllUserResponse(last_page):
    page = last_page +1
    while True:
        print "fetch page : %d" % page
        jsonObj = json.loads(getUserResponse(page))
        if len(jsonObj["directory_items"]) == 0:
            return
        yield jsonObj
        page+=1

#获取所有用户列表和级别并保存
def getAllUser():
    result = False
    engine =  create_engine('mysql://my_db_user:Appuser@01@127.0.0.1:3306/envto_db?charset=utf8', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    schedule = session.query(Schedule).filter_by(id=1).first()
    cur_page = -1
    for jsonObj in getAllUserResponse(schedule.last_user_page_id):
        try:
            print "size :%d" % len(jsonObj["directory_items"])
            for match in  jsonObj["directory_items"]:
                badges_result = getUserBadges(match["user"]["username"])
                if badges_result:
                    badges = json.loads(badges_result)
                else:
                    badges = None
                saveUserRespones(match, badges)
            next_page_obj = jsonObj["load_more_directory_items"]
            
            if next_page_obj is not None:
                cur_page = int(next_page_obj.split("&")[2].split("=")[1])-1
                schedule = session.query(Schedule).filter_by(id=1).first()
                schedule.last_user_page_id = cur_page           
                session.add(schedule)
                session.commit()
        except:
            print sys.exc_info()
            import traceback
            print traceback.print_exc()
            print "fail to fetch page: " + str(cur_page) + "\n"
            break



def saveUserRespones(result, badges):
    rawId = unicode(result["user"]["id"])
    username = unicode(result["user"]["username"])
    avator = unicode(result["user"]["avatar_template"])
    Session = sessionmaker(bind=engine)
    session = Session()
    if session.query(User).filter_by(raw_id=rawId).first():
        print "User of raw id %s already saved\n" % (rawId)
    afflevel = 0
    if badges:
        for badges in badges["user-badges"]:
            if "affiliate_level_" in badges["name"]:
                afflevel = int(badges["name"].replace("affiliate_level_",""))


    user = session.query(User).filter_by(raw_id=rawId).first()
    if not user:
        user = User(rawId, username ,1 , afflevel, avator)
    
    session.add(user)
    session.commit()
    print "saved user " + unicode(rawId).encode("utf-8")

    return 

def saveRespones(result, site_name,session):
    tagObjs = []
    categoryObjs = []
    thumbObjs = []
    descImageObjs = []

    rawId = int(unicode(result["id"]))
    #Session = sessionmaker(bind=engine)
    #session = Session()
    site = session.query(Site).filter_by(name=site_name).first()

    if session.query(Product).filter_by(site_id=site.id).filter_by(raw_id=rawId).first():
        print "Product of raw id %s in site %s already saved\n" % (rawId, site_name)
        return       

    for tagName in result["tags"]:
        tagObj = session.query(Tag).filter_by(site_id=site.id).filter_by(name=tagName).first()
        if not tagObj:
            tagObj = Tag("", tagName, site)
            session.add(tagObj)
        tagObjs.append(tagObj)
            

            

    catName = result["classification"]
    catUrl = result["classification_url"]
    catObj = session.query(Category).filter_by(site_id=site.id).filter_by(name=catName).first()
    if not catObj:
        catObj = Category(catUrl, catName, site)
        session.add(catObj)
        #print u"save" + catObj.__repr__()
    categoryObjs.append(catObj)
       
    thumbs = None
    descImages = None
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

    title = unicode(result["name"])
    url = unicode(result["url"])
    if result["number_of_sales"] is None:
        print "rawid: " + str(rawId) + "'s sales is None"
        number_of_sales = 0
    else:
        number_of_sales = int(unicode(result["number_of_sales"]))

    description = unicode(result["description"])
    description_html = unicode(result["description_html"])
    metainfo = unicode(result)
    author_username = unicode(result["author_username"])
    author_url = unicode(result["author_url"])
    author_image = unicode(result["author_image"])
    rating_count = int(unicode(result["rating"]["count"]))
    rating = float(unicode(result["rating"]["rating"]))
    to_zone = tz.gettz('America/New_York')
    updated_at = parser.parse(unicode(result["updated_at"])).replace(tzinfo=None)
    published_at = parser.parse(unicode(result["published_at"])).replace(tzinfo=None)
    price_cents = int(unicode(result["price_cents"]))

    site_name = unicode(result["site"])
    site = session.query(Site).filter_by(name=site_name).first()
    if not site:
        site = Site("", site_name, site_name)
        session.add(site)
        session.commit()


    product = session.query(Product).filter_by(raw_id=rawId).first()
    if not product:
        product = Product(rawId, site.id, title, description, description_html, metainfo, "", "", "", "", url, \
            number_of_sales, author_username, author_url, author_image, rating_count, rating, updated_at, published_at, price_cents)
    
    for cat in categoryObjs:
        #print (u"cat " + cat.name).encode("utf-8")
        if cat not in product.categories:
            product.categories.append(cat)

    for tag in tagObjs:
        #print (u"tag " + tag.name).encode("utf-8")
        if tag not in product.tags:
            product.tags.append(tag)

   
    session.add(product)
    session.commit()
    print "saved product " + unicode(rawId).encode("utf-8")

    return 


def saveFilter(filter_list, site_name):
    engine =  create_engine('mysql://my_db_user:Appuser@01@127.0.0.1:3306/envto_db?charset=utf8', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    for s_filter in filter_list:
        try:
            if session.query(SearchFilter).filter_by(price_range_filter=str(s_filter)).first():
                print "filter " + str(s_filter) + "is already in database!"
                continue
            d_filter = SearchFilter(pickle.dumps(s_filter))
            site = session.query(Site).filter_by(name=site_name).first()
            d_filter.site_id = site.id
            d_filter.scraped = False
            session.add(d_filter)
            session.commit()
        except:
            print sys.exc_info()
            import traceback
            print traceback.print_exc()
            print "fail to save filter" + str(filter_list)
            break



def startExtract(token, site_name):
    engine =  create_engine('mysql://my_db_user:Appuser@01@127.0.0.1:3306/envto_db?charset=utf8', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    for s_filter in session.query(SearchFilter):
        try:
            if(s_filter.scraped == False and s_filter.site.name == site_name):
                print "scraping ranges: " + str(pickle.loads(s_filter.price_range_filter)) + "\n"
                getFilterRange(pickle.loads(s_filter.price_range_filter), site_name, session)
                s_filter.scraped = True
                session.add(s_filter)
                session.commit()
        except:
            print sys.exc_info()
            import traceback
            print traceback.print_exc()
            print "fail to search：" + str(pickle.loads(s_filter.price_range_filter)) + "\n"
            break

    return 


if __name__ == "__main__":
    #print '\xb7\xa2\xc9\xfa\xd2\xe2\xcd\xe2\xa1\xa3'.encode("GBK")
    token = "NdlBDRUM651s8hhWEQlsUNqPbzC4omhi"
    #getAllUser()
    #checkFilters("videohive.net")

    #print final_filter_list
    #saveFilter(final_filter_list, "videohive.net")
    startExtract(token, "videohive.net")

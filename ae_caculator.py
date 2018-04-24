#coding=utf-8

from urllib2 import urlopen
import urllib
import cookielib
import urllib2
import re
import sqlite3
import ast
import sys
import json
from sqlalchemy.orm import sessionmaker
from theme_models import *
from sqlalchemy import create_engine
import requests
from dateutil import parser,tz
from datetime import datetime
import pickle
import yapi
from sqlalchemy.sql import text


class ApiHelper:
	api_key_dict = {}
	api_key_dict["query"] = "AIzaSyCeYyC9hQB0-dfsh5z_0vPGPV2IpfEhee4"
	api_key_dict["query1"] = "AIzaSyA3UpnW07cIL7yLrEO8pgI9WnpDWVi8Kf8"
	api_key_dict["query2"] = "AIzaSyC-QnwSUhzh7CyFswq9YCRGY5jhbgbLRKM"
	api_key_dict["query3"] = "AIzaSyAGj6INkOkDvsb_WZfK1lm34cXddisf4fw"
	api_key_dict["query4"] = "AIzaSyDz7KjPUx85ZvbJuyaPVChqQI03Xxsh8AY"
	api_key_dict["query6"] = "AIzaSyCkbCT1GQkpLnAkkVifi7gszAalQCSjoi4"
	api_key_dict["query7"] = "AIzaSyC6bEMzpek_htiZmNKq7n388P4VWWLbF1c"
	api_key_dict["query8"] = "AIzaSyAdpDIRsLSlWxQrqiIkZOHOVpFeXtzrmuo"
	api_key_dict["teak-mix-179516"] = "AIzaSyDVo-Gp_vPuFoBMz2AGKVepUoigYsFrVAE"
	current_api_num = -1
	def __init__(self):
		pass
	def get_api(self):
		result = None
		self.current_api_num += 1
		values = self.api_key_dict.values()
		if self.current_api_num <  len(values):
			result = yapi.YoutubeAPI(values[self.current_api_num])
		print "change_to_api:" + values[self.current_api_num]
		return result






def get_youtube_result(api, keyword):
	videos = api.video_search(keyword + " after effect template", max_results=30, order="relevance")
	counts = 0
	if ("items" in videos.__dict__) == False:
		return -1
	for video in videos.__dict__["items"]:
		d_video=video.__dict__["snippet"]
		if keyword.lower() in d_video.__dict__["title"].lower() and ( "template" in d_video.__dict__["channelTitle"].lower() or "effect" in  d_video.__dict__["channelTitle"].lower()):
			counts +=1
	print "get_youtube_result count is :" + str(counts)
	return counts

def extractSampleUrl(product_id, json_txt):
	sample_url=u"None"
	try:
		s_result = json.loads(json.dumps(ast.literal_eval(json_txt)))
		if s_result.has_key("previews"):
			s_result = s_result["previews"]
			if s_result.has_key("icon_with_video_preview"):
				s_result = s_result["icon_with_video_preview"]
				if s_result.has_key("video_url"):
					s_result = s_result["video_url"]
					if unicode(s_result) != u"":
						sample_url = unicode(s_result)
	except:
		print sys.exc_info()
		import traceback
		print traceback.print_exc()
		print "fail to parse:" + str(product_id) + "\n"
		print json_txt
	return sample_url

def updateSampleUrl(site_name):
	engine =  create_engine('mysql://my_db_user:Appuser@01@127.0.0.1:3306/envto_db?charset=utf8', echo=False)
	Session = sessionmaker(bind=engine)
	session =  Session()
	update_session = Session()
	for product in session.query(Product.title,Product.url,Product.id,Product)\
				.join(Product.categories)\
				.filter(Category.name.like("after-effects-project-files%")):
		try:
			new_product=session.query(Product).filter_by(id=product.id).first()
			new_product.sample_url = extractSampleUrl(product.id,new_product.info.metainfo.decode("utf-8"))
			print new_product.sample_url
			session.add(new_product)
			session.commit()

		except:
			print sys.exc_info()
			import traceback
			print traceback.print_exc()
			print "fail to update：" + str(product.url) + "\n"
	session.close()


def startCaculate(site_name):
	engine =  create_engine('mysql://my_db_user:Appuser@01@127.0.0.1:3306/envto_db?charset=utf8', echo=False)
	Session = sessionmaker(bind=engine)
	session =  Session()
	update_session = Session()
	rating_weight = 30.0
	rating_count_weight = 0.1
	updated_weight = 10.0
	search_result_weight = 20.0
	api_helper = ApiHelper()
	api = api_helper.get_api()
	#.filter_by(priority_score=0)
	for product in session.query(Product)\
			 .from_statement(text("select p.* from products as p ,categories as c, product_cat as pc \
                                                where pc.product_id = p.id and pc.category_id = c.id \
                                                and c.name like :categorie_name "))\
             .params(categorie_name='after-effects-project-files%')\
             .all():
		try:
			score = rating_count_weight * float(product.rating_count)
			print "rating_count_weight:" + str(score) + " of " + str(product.rating_count)
			rating = float(product.rating)
			#too few people get lower rating
			if int(product.rating_count) < 15 and int(rating) == 5: 
				rating = 4.3
			score += rating_weight * rating
			print "rating_weight: " + str(score) + " of " + str(product.rating)
			score += updated_weight * (float(str(product.published_at).split("-")[0]) - 2010.0)
			print "published_at_weight: " + str(score) + " of " + str(product.published_at)
			y_result =0
			while True:
				y_result = get_youtube_result(api,product.title)
				if y_result < 0:
				   api = api_helper.get_api()
				   if api is None:
						print "api limits exceed!!：" + str(api) + "\n"
						return
				else:
					break

			score -= search_result_weight * float(y_result)
			print "total socre of " + product.url + " is " + str(int(score))
			new_product=session.query(Product).filter_by(id=product.id).first()
			new_product.priority_score = int(score)
			session.add(new_product)
			session.commit()
		except:
			print sys.exc_info()
			import traceback
			print traceback.print_exc()
			print "fail to search：" + str(product.url) + "\n"
	session.close()

	return 


if __name__ == "__main__":
	#print '\xb7\xa2\xc9\xfa\xd2\xe2\xcd\xe2\xa1\xa3'.encode("GBK")
	token = "NdlBDRUM651s8hhWEQlsUNqPbzC4omhi"
	#getAllUser()
	#checkFilters("videohive.net")

	#print final_filter_list
	#saveFilter(final_filter_list, "videohive.net")
	startCaculate("videohive.net")
	#updateSampleUrl("videohive.net")

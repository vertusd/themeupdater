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
import yapi








def startMoving(site_name):
	engine =  create_engine('mysql://my_db_user:Appuser@01@127.0.0.1:3306/envto_db?charset=utf8', echo=False)
	Session = sessionmaker(bind=engine)
	session =  Session()
	update_session = Session()
	for product in session.query(Product.id):
		try:
			old_product=update_session.query(Product).filter_by(id=product.id).first()
			product_info = ProductInfo(old_product.description,old_product.description_html,old_product.metainfo)
			update_session.add(product_info)
			update_session.commit()
			old_product.info_id = product_info.id
			update_session.add(old_product)
			update_session.commit()
		except:
			print sys.exc_info()
			import traceback
			print traceback.print_exc()
			print "fail to search：" + str(product.url) + "\n"
	session.close()
	update_session.close()

	return 


if __name__ == "__main__":
	#print '\xb7\xa2\xc9\xfa\xd2\xe2\xcd\xe2\xa1\xa3'.encode("GBK")

	startMoving("videohive.net")

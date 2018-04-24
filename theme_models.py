from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, ForeignKey,JSON,Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
import os
import datetime
Base = declarative_base()
cur_dir = os.path.abspath('.')
engine = create_engine('mysql://my_db_user:Appuser@01@127.0.0.1:3306/envto_db?charset=utf8', echo=False)




class State():
    NOT_SCRAPED = 0
    SCRAPING = 1
    SCRAPED = 2
    SCRAPFAILED = 3
    DOWNLOADING =4
    DOWNLOADED =5
    DOWNLOADFAILED=6
    UPLOADING=8
    UPLOADED=8
    UPLOADFAILED=9
    UPDATINGDB= 10
    UPDATEDDB =11
    UPDATEDBFAILED =12
    UPDATINGBLOG = 13
    UPDATEDBLOG =14
    UPDATEDBLOGFAILED =15
    FINISHED = 16
    FAILED = 17


class SearchFilter(Base):
    __tablename__ = 'search_filters'
    id = Column(Integer, primary_key=True, autoincrement=True)
    price_range_filter = Column(String(1000), nullable=False)
    scraped =  Column(Boolean, nullable=False, default=False)
    site_id = Column(Integer, ForeignKey('sites.id'))
    site = relationship("Site", backref=backref('search_filters', order_by=id))
    
    def __init__(self, price_range_filter):
        self.price_range_filter = price_range_filter

    def __repr__(self):
        return "<Price('%s')>" % ( self.price_range_filter)

class Site(Base):
    __tablename__ = 'sites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(10000))


    def __init__(self, site_url,name, description=""):
         self.url = site_url
         self.name = name
         self.description = description

    def __repr__(self):
        return "<Site('%s')>" % (self.url)


product_tag_table = Table('product_tag', Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('tag_id', Integer, ForeignKey('tags.id')),
    Column('product_id', Integer, ForeignKey('products.id'))
)

product_cat_table = Table('product_cat', Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('category_id', Integer, ForeignKey('categories.id')),
    Column('product_id', Integer, ForeignKey('products.id'))
)


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    url =  Column(String(1000), nullable=False)
    site_id = Column(Integer, ForeignKey('sites.id'))
    site = relationship("Site", backref=backref('tags', order_by=id))
    description = Column(String(1000))

    def __init__(self, url,name,site, description=""):
         self.url = url
         self.name = name
         self.site = site
         self.description = description

    def __repr__(self):
        return self.name
        #return "<Tag('%s','%s')>" % (self.url, self.name)


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    url =  Column(String(1000), nullable=False)
    site_id = Column(Integer, ForeignKey('sites.id'))
    site = relationship("Site", backref=backref('categories', order_by=id))
    description = Column(String(1000))

    def __init__(self, url,name,site, description=""):
         self.url = url
         self.name = name
         self.site = site
         self.description = description

    def __repr__(self):
        return self.name
       # return "<Category('%s','%s')>" % (self.url, self.name)

class RemoteUrl(Base):
    __tablename__ = 'remote_urls'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(100), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    product = relationship("Product", backref=backref('remote_url', order_by=id))
    description = Column(Text)

    def __init__(self, url, description=""):
         self.url = url
         self.description = description

    def __repr__(self):
        return "<RemoteUrl('%s')>" % (self.url)

class DescImage(Base):
    __tablename__ = 'desc_images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(1000), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    description = Column(String(1000))
    product = relationship("Product", backref=backref('desc_images', order_by=id))


    def __init__(self, url, description=""):
         self.url = url
         self.description = description

    def __repr__(self):
        return "<DescImage('%s')>" % (self.url)

class ThumbImage(Base):
    __tablename__ = 'thumb_images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(1000), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    description = Column(String(1000))
    product = relationship("Product", backref=backref('thumb_images', order_by=id))


    def __init__(self, url, description=""):
         self.url = url
         self.description = description

    def __repr__(self):
        return "<ThumbImage('%s')>" % (self.url)


class ProductInfo(Base):
    __tablename__ = 'product_infos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text)
    description_html = Column(Text)
    metainfo = Column(JSON)

    def __init__(self, description, description_html, metainfo):
        self.description = description
        self.description_html = description_html
        self.metainfo = metainfo
    def __repr__(self):
        return "<ProductInfo('%s')>" % (self.description)

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_id = Column(Integer,unique = True)
    site_id = Column(Integer, ForeignKey('sites.id'))
    site = relationship("Site", backref=backref('products', order_by=id))
    categories = relationship("Category", secondary=product_cat_table, backref='products')
    tags = relationship("Tag", secondary=product_tag_table, backref='products')
    title = Column(String(1000))
    #description = Column(Text)
    #description_html = Column(Text)
    #metainfo = Column(JSON)
    info_id = Column(Integer, ForeignKey('product_infos.id'))
    info = relationship("ProductInfo", backref=backref('products', order_by=id))
    state = Column(Integer)
    url = Column(String(1000))
    number_of_sales = Column(Integer)
    price_cents = Column(Integer)
    number_of_sales = Column(Integer)
    author_username = Column(String(500))
    author_url= Column(String(500))
    author_image= Column(String(500))
    rating_count = Column(Integer)
    rating = Column(Float)
    updated_at =  Column(DateTime)
    published_at =  Column(DateTime)

    header_url_hd = Column(String(1000))
    header_url_md  = Column(String(1000))
    header_url_sd = Column(String(1000))
    sample_url = Column(String(1000))
    priority_score = Column(Integer,default=0)
    uploaded =  Column(Boolean, nullable=False, default=False)


    def __init__(self, raw_id, site_id, title, description, description_html, metainfo, header_url_hd="", header_url_md="", \
               header_url_sd="", sample_url="",url="",number_of_sales=0, author_username="", author_url="", \
               author_image="", rating_count=0,  rating=1, updated_at=datetime.datetime.now(), published_at=datetime.datetime.now(), price_cents=0):
     self.raw_id = raw_id
     self.site_id = site_id
     self.title = title
     self.description = description
     self.description_html = description_html
     self.header_url_hd = header_url_hd
     self.header_url_md = header_url_md
     self.header_url_sd = header_url_sd
     self.sample_url = sample_url
     self.url = url
     self.number_of_sales = number_of_sales
     self.author_username = author_username
     self.author_url = author_url
     self.author_image = author_image
     self.rating_count = rating_count
     self.rating = rating
     self.updated_at = updated_at
     self.published_at = published_at
     self.metainfo = metainfo
     self.price_cents = price_cents

    def __repr__(self):
        return u"<Product('%s','%s', '%s')>" % (self.site_id, self.title, self.raw_id)


class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True, autoincrement=True)
    last_product_id = Column(String(1000))
    last_user_page_id = Column(Integer)
    last_task_state = Column(Integer)
    product_perday = Column(Integer)
    retry_times = Column(Integer)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(Integer, ForeignKey('sites.id'))
    site = relationship("Site", backref=backref('users', order_by=id))
    raw_id = Column(String(500))
    name  = Column(String(500))
    afflevel = Column(Integer)
    avatar_url = Column(String(500))
    comment = Column(String(100))

    def __init__(self, raw_id, name, site_id, afflevel=0, avatar_url=""):
         self.raw_id = raw_id
         self.name = name
         self.site_id = site_id
         self.afflevel = afflevel
         self.avatar_url = avatar_url

    def __repr__(self):
        return "<User('%s','%s')>" % (self.name, self.afflevel)

if __name__ == "__main__":
    Base.metadata.create_all(engine)

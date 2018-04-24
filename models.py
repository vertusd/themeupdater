from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy import create_engine
import os

Base = declarative_base()
cur_dir = os.path.abspath('.')
engine = create_engine('mysql://feti:feti123456@192.64.114.146:3306/feti?charset=utf8', echo=False)






class State():
    NOT_DOWNLOADED = 0
    DOWNLOADING = 1
    DOWNLOADED = 2
    DOWNLOADFAILED = 3
    CONVERTING = 4
    CONVERTED = 5
    CONVERTFAILED = 6
    UPLOADING = 7
    UPLOADED = 8
    UPLOADFAILED = 9
    UPDATINGDB= 10
    UPDATEDDB =11
    UPDATEDBFAILED =12
    UPDATINGBLOG = 13
    UPDATEDBLOG =14
    UPDATEDBLOGFAILED =15
    FINISHED = 16
    FAILED = 17

class VideoType(Base):
    __tablename__ = 'video_types'

    id =  Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    bitrate = Column(String(30))
    is_sample = Column(Boolean, nullable=False)


class RemoteStorage(Base):
    __tablename__ = 'remote_storages'
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(1000))
    login = Column(String(100), nullable=False)
    passwd = Column(String(100), nullable=False)
    enabled = Column(Boolean,nullable=False)
     
 
    def __init__(self, url,name, description=""):
         self.url = url
         self.name = name
         self.description = description
 
    def __repr__(self):
        return "<RemoteStorage('%s')>" % (self.url)

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


movie_tag_table = Table('movie_tag', Base.metadata,
    Column('tag_id', Integer, ForeignKey('tags.id')),
    Column('movie_id', Integer, ForeignKey('movies.id'))
)

movie_cat_table = Table('movie_cat', Base.metadata,
    Column('category_id', Integer, ForeignKey('categories.id')),
    Column('movie_id', Integer, ForeignKey('movies.id'))
)

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    url =  Column(String(1000), nullable=False)
    #site_id = Column(Integer, ForeignKey('sites.id'))
    #site = relationship("Site", backref=backref('tags', order_by=id))
    description = Column(String(1000))
 
    def __init__(self, url,name, description=""):
         self.url = url
         self.name = name
         self.description = description
 
    def __repr__(self):
        return "<Tag('%s','%s')>" % (self.url, self.name)


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    url =  Column(String(1000), nullable=False)
    #site_id = Column(Integer, ForeignKey('sites.id'))
    #site = relationship("Site", backref=backref('categories', order_by=id))
    description = Column(String(1000))
 
    def __init__(self, url,name, description=""):
         self.url = url
         self.name = name
         self.description = description
 
    def __repr__(self):
        return "<Category('%s','%s')>" % (self.url, self.name)

class RemoteUrl(Base):
    __tablename__ = 'remote_urls'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(100), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    remote_storage_id = Column(Integer, ForeignKey('remote_storages.id'), nullable=False)
    video_type_id = Column(Integer, ForeignKey('video_types.id'), nullable=False)
    movie = relationship("Movie", backref=backref('remote_url', order_by=id))
    remote_storage = relationship("RemoteStorage", backref=backref('remote_url', order_by=id))
    video_type = relationship("VideoType", backref=backref('remote_url', order_by=id))
    description = Column(String(100000))
 
    def __init__(self, url, description=""):
         self.url = url
         self.description = description
 
    def __repr__(self):
        return "<RemoteUrl('%s')>" % (self.url)

class DescImage(Base):
    __tablename__ = 'desc_images'
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(1000), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    description = Column(String(1000))
    movie = relationship("Movie", backref=backref('desc_images', order_by=id))
     
 
    def __init__(self, url, description=""):
         self.url = url
         self.description = description
 
    def __repr__(self):
        return "<DescImage('%s')>" % (self.url)

class ThumbImage(Base):
    __tablename__ = 'thumb_images'
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(1000), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    description = Column(String(1000))
    movie = relationship("Movie", backref=backref('thumb_images', order_by=id))
     
 
    def __init__(self, url, description=""):
         self.url = url
         self.description = description
 
    def __repr__(self):
        return "<ThumbImage('%s')>" % (self.url)


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_id = Column(Integer)
    #site_id = Column(Integer, ForeignKey('sites.id'))
    #site = relationship("Site", backref=backref('movies', order_by=id))
    #category_id = Column(Integer, ForeignKey('categories.id'))
    #category = relationship("Category", backref=backref('movies', order_by=id))
    categories = relationship("Category", secondary=movie_cat_table, backref='movies')
    tags = relationship("Tag", secondary=movie_tag_table, backref='movies')
    title = Column(String(1000))
    movie_url_hd = Column(String(1000))
    movie_url_md  = Column(String(1000))
    movie_url_sd = Column(String(1000))
    sample_url = Column(String(1000))
    description = Column(String(100000))
    state = Column(Integer)



    def __init__(self, raw_id, title,description, movie_url_hd="", movie_url_md="", movie_url_sd="",sample_url=""):
     self.raw_id = raw_id
     #self.site_id = site_id
     self.title = title
     self.description = description
     self.movie_url_hd = movie_url_hd
     self.movie_url_md = movie_url_md
     self.movie_url_sd = movie_url_sd
     self.sample_url = sample_url

    def __repr__(self):
        return u"<Movie('%s','%s', '%s')>" % (self.site_id, self.title, self.raw_id)


class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True, autoincrement=True)
    last_movie_id = Column(Integer)
    last_task_state = Column(Integer)
    movies_perday = Column(Integer)
    retry_times = Column(Integer)


if __name__ == "__main__":
    Base.metadata.create_all(engine)

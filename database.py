from sqlalchemy import create_engine, Table, Column, Integer, String, Boolean, MetaData, select
import urlparse

DB_NAME = 'scraper.sqlite'


class ScraperDb:

	def __init__(self):
		self.connected = False
		#connect();
		
	def connect(self):
		self.engine = create_engine('sqlite:///' + DB_NAME)
		self.connection = self.engine.connect()
		self.connected = True if self.connection else False
		self.metadata = MetaData()

		#!!!TODO!!!
		#Define the tables
		self.website_table = Table('website', self.metadata,
			Column('id', Integer, primary_key=True),
			Column('url', String, nullable=False),
			Column('has_crawled', Boolean, default=False),
			Column('emails', String, nullable=True),
		)

		#Create the tables
		self.metadata.create_all(self.engine)
		
		
		
db = ScraperDb()		
db.connect()
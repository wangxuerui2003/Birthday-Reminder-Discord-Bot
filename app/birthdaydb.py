import datetime
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError, InterfaceError
from sqlalchemy.orm import sessionmaker
import os

class BirthdayDB():
	def __init__(self):
		self.db_user = os.getenv('MYSQL_USER')
		self.db_pwd = os.getenv('MYSQL_PASSWORD')
		self.db_host = os.getenv('MYSQL_HOST')
		self.db_port = os.getenv('MYSQL_PORT')
		self.db_name = os.getenv('MYSQL_DATABASE')
		self.db_conn_success = True
		self.connect_db()
		if self.db_conn_success:
			self.create_table()
			self.SessionObj = sessionmaker(bind=self.engine)
			self.session = self.SessionObj()


	def __del__(self): # close connection and dispose engine in the destructor
		if self.db_conn_success:
			self.con.close()
			self.engine.dispose()
	
	def create_table(self):
		if len(self.con.execute(text("SELECT * FROM information_schema.TABLES WHERE TABLE_NAME = 'Birthdays'")).fetchall()) > 0: # if table already exists
			return
		with open("./db_queries/createtable.sql", 'r') as f: # execute the createtable.sql query
			query = text(f.read())
			self.con.execute(query)

	def connect_db(self):
		self.engine: sqlalchemy.Engine = create_engine(f'mysql+mysqlconnector://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_name}')

		try:
			try:
				self.con = self.engine.connect()
			except ProgrammingError as e:
				print(e)
				self.engine.dispose() # dispose the previous engine since the database doesn't exist
				self.engine = create_engine(f'mysql+mysqlconnector://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/mysql') # connect to a for sure db first
				con: sqlalchemy.Connection = self.engine.connect() # setup connection
				with open('./db_queries/createdb.sql', 'r') as f: # execute the createdb.sql query
					query = text(f.read())
					con.execute(query)
				self.engine.dispose() # dispose the useless engine again

				# create the final engine and connection
				self.engine = self.engine = create_engine(f'mysql+mysqlconnector://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_name}')
				self.con = self.engine.connect()
		except InterfaceError as e:
			self.db_conn_success = False


	def store_birthday(self, username, birthday, user):
		if self.birthday_exists(user):
			return
		query = text('INSERT INTO Birthdays (user_id, username, birthday) VALUES (:user_id, :username, :birthday)')
		self.session.execute(query, {'user_id': str(user.id), 'username': username, 'birthday': birthday})
		self.session.commit()

	def get_birthdays(self):
		self.session.expire_all()
		self.session = self.SessionObj()
		return self.session.execute(text('SELECT * from Birthdays')).fetchall()

	def birthday_exists(self, user):
		self.session.expire_all()
		self.session = self.SessionObj()
		if len(self.session.execute(text('SELECT user_id from Birthdays WHERE user_id = :user_id'), {"user_id": str(user.id)}).fetchall()) > 0:
			return True
		return False
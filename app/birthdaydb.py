import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
import os

class BirthdayDB():
	def __init__(self):
		self.db_user = os.getenv('MYSQL_USER')
		self.db_pwd = os.getenv('MYSQL_PASSWORD')
		self.db_host = os.getenv('MYSQL_HOST')
		self.db_port = os.getenv('MYSQL_PORT')
		self.db_name = os.getenv('MYSQL_DATABASE')
		self.connect_db()
		self.create_table()

	def __del__(self): # close connection and dispose engine in the destructor
		self.con.close()
		self.engine.dispose()
	
	def create_table(self):
		if len(self.con.execute(text("SELECT * FROM information_schema.TABLES WHERE TABLE_NAME = 'Birthdays'")).fetchall()) > 0: # if table already exists
			return
		with open("./db_queries/createtable.sql", 'r') as f: # execute the createtable.sql query
			query = text(f.read())
			self.con.execute(query)

	def connect_db(self):
		self.engine = create_engine(f'mysql+mysqlconnector://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_name}')

		try:
			self.con = self.engine.connect()
		except ProgrammingError as e:
			print(e)
			self.engine.dispose() # dispose the previous engine since the database doesn't exist
			self.engine = create_engine(f'mysql+mysqlconnector://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/mysql') # connect to a for sure db first
			con = self.engine.connect() # setup connection
			with open('./db_queries/createdb.sql', 'r') as f: # execute the createdb.sql query
				query = text(f.read())
				con.execute(query)
			self.engine.dispose() # dispose the useless engine again

			# create the final engine and connection
			self.engine = self.engine = create_engine(f'mysql+mysqlconnector://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_name}')
			self.con = self.engine.connect()


	def store_birthday(self, birthday, user):
		if self.birthday_exists(user):
			return
		query = text('INSERT INTO Birthdays (user_id, birthday) VALUES (:user_id, :birthday)')
		self.con.execute(query, {'user_id': str(user.id), 'birthday': birthday})
		self.con.commit()

	def get_birthdays(self):
		return self.con.execute(text('SELECT * from Birthdays')).fetchall()

	def birthday_exists(self, user):
		if len(self.con.execute(text('SELECT user_id from Birthdays WHERE user_id = :user_id'), {"user_id": str(user.id)}).fetchall()) > 0:
			return True
		return False
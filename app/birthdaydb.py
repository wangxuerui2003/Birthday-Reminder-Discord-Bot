import datetime
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError, InterfaceError
from sqlalchemy.orm import sessionmaker
import os
import discord

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
	
	def create_table(self) -> None:
		"""
			Create the table the first time connected to the database.
		"""

		if len(self.con.execute(text("SELECT * FROM information_schema.TABLES WHERE TABLE_NAME = 'Birthdays'")).fetchall()) > 0: # if table already exists
			return
		with open("./db_queries/createtable.sql", 'r') as f: # execute the createtable.sql query
			query = text(f.read())
			self.con.execute(query)

	def connect_db(self) -> None:
		"""
			Connect to the mysql database.
			If not successful, means the credentials are incorrect or database doesn't exist.
				If credentials are wrong or mysql server doesn't exist, then put db_conn_success to False and main.py will exit the program.
				If database doesn'e exist, then create the database in the mysql server.
		"""

		self.engine: sqlalchemy.Engine = create_engine(f'mysql+mysqlconnector://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_name}')
		try:
			try:
				self.con: sqlalchemy.Connection = self.engine.connect()
			except ProgrammingError as e:
				print(e)
				self.engine.dispose() # dispose the previous engine since the database doesn't exist
				self.engine: sqlalchemy.Engine = create_engine(f'mysql+mysqlconnector://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/mysql') # connect to a for sure db first
				con: sqlalchemy.Connection = self.engine.connect() # setup connection
				with open('./db_queries/createdb.sql', 'r') as f: # execute the createdb.sql query
					query = text(f.read())
					con.execute(query)
				self.engine.dispose() # dispose the useless engine again

				# create the final engine and connection
				self.engine = self.engine = create_engine(f'mysql+mysqlconnector://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_name}')
				self.con = self.engine.connect()
		except InterfaceError as e:
			self.db_conn_success: bool = False


	def store_birthday(self, username: str, birthday: datetime.date, user: str) -> None:
		"""
			Insert a row of birthday info into the database if the user haven't set his/her birthday yet.
		"""

		if self.birthday_exists(user):
			return
		query = text('INSERT INTO Birthdays (user_id, username, birthday) VALUES (:user_id, :username, :birthday)')
		self.session.execute(query, {'user_id': str(user.id), 'username': username, 'birthday': birthday})
		self.session.commit()

	def get_birthdays(self) -> list[tuple]:
		"""
			Create a new db session to get up to date info and return a list of birthday info rows.
		"""

		self.session.expire_all()
		self.session = self.SessionObj()
		return self.session.execute(text('SELECT * from Birthdays')).fetchall()

	def birthday_exists(self, user: discord.User) -> bool:
		"""
			If the number of rows returned when select user_id from Birthdays table is greater than 0,
			means the user exists in the db, then return True. Else return False.
		"""

		self.session.expire_all()
		self.session = self.SessionObj()
		return len(self.session.execute(text('SELECT user_id from Birthdays WHERE user_id = :user_id'), {"user_id": str(user.id)}).fetchall()) > 0
import datetime

class DbOperator():
	def __init__(self, connector):
		self.connector = connector
		self.cursor = self.connector.cursor()
		# TODO: create database "discordbotDB" and table "Birthdays"

	def __del__(self):
		self.cursor.close()
		self.connector.close()
	
	def store_birthday(self, birthday):
		pass

	def get_birthdays(self):
		pass

	def birthday_exists(self, user):
		return False
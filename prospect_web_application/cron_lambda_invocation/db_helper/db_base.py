from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from GlobalVariables import (
								DB_HOST,
								DB_USER,
								DB_PASSWORD,
								DB_NAME
							)


class DBConnector():

	def __init__(self):
		self.engine = create_engine('postgresql+psycopg2://{user}:{password}@{host}/{db_name}'.format(
																							user=DB_USER,
																							password=DB_PASSWORD,
																							host=DB_HOST,
																							db_name=DB_NAME
																						))

		self.Session = sessionmaker(bind=self.engine)

		self.Base = declarative_base()

	def get_engine(self):
		return self.engine


	def get_session(self):
		return self.Session

	def get_declarative_base(self):
		return self.Base


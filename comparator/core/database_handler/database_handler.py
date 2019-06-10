import MySQLdb

class DatabaseHandler(object):

	def __init__(self,db_settings, comparison_id):
		self.comparison_id = comparison_id
		self.connection = MySQLdb.connect(host=db_settings['HOST'],port=int(db_settings['PORT']),db=db_settings['NAME'],user=db_settings['USER'],passwd=db_settings['PASSWORD'])


	def save_project_status(self,project_status,error_count):
		self.cursor = self.connection.cursor()

		update_statement = "update engine_projectcomparator set project_status ='{}',error_count={} where id={}".format(project_status,error_count,self.comparison_id)
		
		try:
		   # Execute the SQL command
		   self.cursor.execute(update_statement)
		   # Commit your changes in the database
		   self.connection.commit()

		except Exception:
		   # Rollback in case there is any error
		   self.connection.rollback()


	def close_database(self):
		self.connection.close()


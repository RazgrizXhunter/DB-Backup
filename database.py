import mysql.connector, logging

logger = logging.getLogger("logger")

class database:
	connection = None

	def __init__(self, host, user, password, database):
		self.connection = mysql.connector.connect(host, user, password, database)
	
	def weight(database_name):
		if (connection == None): return logger.error("Not connected to the database")
		
		cursor = connection.cursor()

		statement = """
					SELECT table_schema "DB Name",
					ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) "DB Size in MB" 
					FROM information_schema.tables 
					GROUP BY table_schema;
					"""
		
		cursor.execute(statement)
		result = cursor.fetchall() #ferchone()

		for entry in result:
			print(entry)
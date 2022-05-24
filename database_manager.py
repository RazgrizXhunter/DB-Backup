import sys, os, subprocess, time, logging, re

logger = logging.getLogger("logger")

class Database_manager:
	config = None

	def __init__(self, config):
		self.config = config
	
	def dump(self, schema: str, extension: str = "sql"):
		logger.info(f"Attempting dump of schema: {schema}")

		if (self.config == None):
			return logger.warning("You need to load the config file first!")
		
		if (not os.path.isdir(self.config["backup"]["target_directory"])):
			logger.warning("Specified target directory doesn't exist. Creating...")
			try:
				os.mkdir(self.config["backup"]["target_directory"])
			except Exception as e:
				logger.error("Directory could not be created")
				logger.error(e)
				sys.exit()
		
		file_path = "{target_directory}/backup_{schema}_{timestamp}.{extension}".format(
			target_directory = self.config["backup"]["target_directory"],
			schema = schema,
			timestamp = time.strftime('%Y-%m-%d_%H-%M-%S'),
			extension = extension
		)
		
		command = "mysqldump -u{user} -p\'{password}\' {schema} > {file_path}".format(
			user = self.config["database"]["user"],
			password = self.config["database"]["password"],
			schema = schema,
			file_path = file_path
		)

		logger.info(f"dumping on {file_path}")

		try:
			subprocess.run(command, capture_output=True, shell=True)
			logger.info("Dump complete!")
		except Exception as e:
			logger.error(e)
			sys.exit()
		
		return file_path
	
	def get_schema_size(self, schema: str):
		logger.info(f"Attempting to weigh schema: {schema}")

		if (self.config == None):
			return logger.warning("You need to load the config file first!")
		
		command = "mysqldump -u{user} -p\'{password}\' {schema} | wc -c".format(
			user = self.config["database"]["user"],
			password = self.config["database"]["password"],
			schema = schema
		)

		try:
			size_bytes = subprocess.run(command, capture_output=True, shell=True).stdout
			logger.info("Weigh complete!")
			return int(re.sub("[^0-9]", "", str(size_bytes)))
		except Exception as e:
			logger.error(e)
			sys.exit()

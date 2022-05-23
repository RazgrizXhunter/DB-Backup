import sys, os, subprocess, time, yaml, logging, re

logger = logging.getLogger("logger")

class s3_backer:
	config = None

	# def __init__(self):

	def load_config(self, filename: str):
		project_dir = os.path.realpath(os.path.dirname(__file__))
		config_file_path = os.path.join(project_dir, filename)

		logger.info(f"Opening config file in: {config_file_path}")

		with open(config_file_path) as f:
			try:
				self.config = yaml.safe_load(f)
				logger.info("Loaded")
			except yaml.YAMLError as error:
				logger.error(format(error))
				sys.exit()
	
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
		
		command = "mysqldump -u{user} -p\'{password}\' {schema}".format(
			user = self.config["database"]["user"],
			password = self.config["database"]["password"],
			schema = schema
		)

		logger.info(f"dumping on {file_path}")

		try:
			dump = subprocess.run(command, capture_output=True, shell=True)
			logger.info("Dump complete!")
		except Exception as e:
			logger.error(e)
			sys.exit()
		
		with open(file_path, "w") as file:
			file.write(dump.stdout.decode("utf-8"))
			file.close()
		
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

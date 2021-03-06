import os, subprocess, logging, re
from modules.configuration_manager import Configuration_manager

logger = logging.getLogger("logger")

class Database_manager:
	def __init__(self) -> None:
		confmanager = Configuration_manager()
		self.config = confmanager.config
	
	def dump_schema(self, schema: str, extension: str = "sql") -> str:
		logger.info(f"Attempting dump of schema: {schema}")

		if (self.config == None):
			logger.warning("You need to load the config file first!")
			return False
		
		if (not os.path.isdir(self.config["backup"]["target_directory"])):
			logger.warning("Specified target directory doesn't exist. Creating...")
			try:
				os.mkdir(self.config["backup"]["target_directory"])
			except Exception as e:
				logger.critical(f"Directory could not be created.\n\t{e}")
		
		file_path = "{target_directory}/{schema}.{extension}".format(
			target_directory = self.config["backup"]["target_directory"],
			schema = schema,
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
			logger.error(f"Dump could not be performed.\n\t{e}")
			return False
		
		return file_path
	
	def get_schema_size(self, schema: str) -> int:
		logger.info(f"Attempting to weigh schema: {schema}")

		if (not self.config):
			logger.error("You need to load the config file first!")
			return False

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
			logger.error(f"Could not weigh current schema.\n\t{e}")
			return False

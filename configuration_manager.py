import os, sys, logging, yaml

logger = logging.getLogger("logger")

class Configuration_manager:

	def __init__(self, filename: str):
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
	
	def getRecipients(self):
		# Pythonics
		return [tuple(reversed(tuple(value for value in dictionary.values() if value is not None))) for dictionary in self.config["responsibles"]]
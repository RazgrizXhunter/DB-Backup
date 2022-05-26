import os, sys, logging, yaml

logger = logging.getLogger("logger")

class Configuration_manager_meta(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			instance = super().__call__(*args, **kwargs)
			cls._instances[cls] = instance
		return cls._instances[cls]

class Configuration_manager(metaclass=Configuration_manager_meta):
	config = None

	def load_config(self, filename: str):
		project_dir = os.path.realpath(os.path.dirname(__file__))
		config_file_path = os.path.join(project_dir, filename)

		logger.info(f"Opening config file in: {config_file_path}")

		with open(config_file_path) as config_file:
			try:
				self.config = yaml.safe_load(config_file)
				logger.info("Loaded")
			except yaml.YAMLError as error:
				logger.critical(f"Configuration file could not be safely loaded.\n\t{format(error)}")
	
	def get_recipients(self) -> list:
		if (self.config == None):
			return False
		
		# Pythonics
		return [tuple(reversed(tuple(value for value in dictionary.values() if value is not None))) for dictionary in self.config["responsibles"]]
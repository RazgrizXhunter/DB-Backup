import os, sys, logging, yaml, datetime
from file_manager import File_manager

logger = logging.getLogger("logger")

class Configuration_manager_meta(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			instance = super().__call__(*args, **kwargs)
			cls._instances[cls] = instance
		return cls._instances[cls]

class Configuration_manager(metaclass=Configuration_manager_meta):
	config = {}
	registry = {}

	def load_config(self, filename: str) -> bool:
		project_dir = os.path.realpath(os.path.dirname(__file__))
		config_file_path = os.path.join(project_dir, filename)

		logger.info(f"Opening config file in: {config_file_path}")

		with open(config_file_path) as config_file:
			try:
				self.config = yaml.safe_load(config_file)
				logger.info("Loaded")
			except yaml.YAMLError as error:
				logger.critical(f"Configuration file could not be safely loaded.\n\t{format(error)}")
		
		return True
	
	def load_registry(self, filename: str):
		project_dir = os.path.realpath(os.path.dirname(__file__))
		registry_file_path = os.path.join(project_dir, filename)

		logger.info(f"Opening registry file in: {registry_file_path}")
		filemanager = File_manager()

		if (not filemanager.exists(registry_file_path)):
			logger.warning(f"Registry file doesn't exist, creating...")

			try:
				with open(registry_file_path, "a") as file:
					file.close()
					logger.debug(f"Registry file created.")
			except Exception as e:
				logger.critical("Could not create registry.")
		
		with open(registry_file_path, "r") as registry_file:
			try:
				self.registry = yaml.safe_load(registry_file) or {}
			except yaml.YAMLError as error:
				logger.critical(f"Registry file could not be safely loaded.\n\t{format(error)}")
		
		return True
	
	def save_registry(self):
		if (not self.registry):
			logger.warning("You can't save an empty registry")
		
		try:
			with open("registry.yaml", "w") as registry_file:
				yaml.dump(self.registry, registry_file)
		except Exception as e:
			logger.critical(f"Could not save registry.\n\t{e}")
		
		return True
	
	def has_entry(self, key):
		if (not self.registry):
			logger.warning("Registry not loaded")
			return False
		
		if (key in self.registry):
			return True
		
		return False
	
	def new_entry(self, key):
		self.registry[key] = datetime.datetime.fromtimestamp(0)
		self.save_registry()
		return self.registry[key]
	
	def update_entry(self, key):
		self.registry[key] = datetime.datetime.today()
		return True
	
	def get_recipients(self) -> list:
		if (self.config == None):
			return False
		
		# Pythonics
		return [tuple(reversed(tuple(value for value in dictionary.values() if value is not None))) for dictionary in self.config["responsibles"]]
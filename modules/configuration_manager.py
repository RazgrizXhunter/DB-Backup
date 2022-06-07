import os, sys, logging, yaml, datetime
from modules.file_manager import File_manager

logger = logging.getLogger("logger")

class Configuration_manager_meta(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			instance = super().__call__(*args, **kwargs)
			cls._instances[cls] = instance
		return cls._instances[cls]

class Configuration_manager(metaclass = Configuration_manager_meta):
	config_path = None
	registry_path = None

	def load_config(self, absolute_path: str) -> bool:
		self.config_path = absolute_path

		logger.info(f"Opening config file in: {self.config_path}")

		with open(self.config_path) as config_file:
			try:
				self.config = yaml.safe_load(config_file)
				logger.info("Loaded")
			except yaml.YAMLError as error:
				logger.critical(f"Configuration file could not be safely loaded.\n\t{format(error)}")
		
		return True
	
	def load_registry(self, absolute_path: str) -> bool:
		self.registry_path = absolute_path

		logger.info(f"Opening registry file in: {self.registry_path}")
		filemanager = File_manager()

		if (not filemanager.exists(self.registry_path)):
			logger.warning(f"Registry file doesn't exist, creating...")

			try:
				with open(self.registry_path, "a") as file:
					file.close()
					logger.debug(f"Registry file created.")
			except Exception as e:
				logger.critical("Could not create registry.")
				return False
		
		with open(self.registry_path, "r") as registry_file:
			try:
				self.registry = yaml.safe_load(registry_file) or {}
			except yaml.YAMLError as error:
				logger.critical(f"Registry file could not be safely loaded.\n\t{format(error)}")
				return False
		
		return True
	
		
		return True
	
	def save_registry(self):
		if (not self.registry):
			logger.warning("You can't save an empty registry")
		
		try:
			with open(self.registry_path, "w") as registry_file:
				yaml.dump(self.registry, registry_file)
		except Exception as e:
			logger.critical(f"Could not save registry.\n\t{e}")
		
		return True
	
	def has_entry(self, key) -> bool:
		key = key.replace(" ", "_")
		if (not self.registry):
			logger.warning("Registry not loaded or empty")
			return False
		
		if (key in self.registry):
			return True
		
		return False
	
	def new_entry(self, key):
		key = key.replace(" ", "_")
		self.registry[key] = datetime.datetime.fromtimestamp(0)
		self.save_registry()
		return self.registry[key]
	
	def update_entry(self, key):
		key = key.replace(" ", "_")
		self.registry[key] = datetime.datetime.today()
		self.save_registry()
		return True
	
	def get_entry(self, key):
		key = key.replace(" ", "_")
		return self.registry[key]
	
	def get_recipients(self) -> list:
		if (self.config == None):
			return False
		
		# Pythonics
		return [tuple(reversed(tuple(value for value in dictionary.values() if value is not None))) for dictionary in self.config["responsibles"]]
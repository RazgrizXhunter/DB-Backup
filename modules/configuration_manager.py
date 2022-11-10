import os, logging, yaml, datetime, re
from modules.file_manager import File_manager
from modules.aws import AWS

logger = logging.getLogger("logger")

class Configuration_manager_meta(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			instance = super().__call__(*args, **kwargs)
			cls._instances[cls] = instance
		return cls._instances[cls]

class Configuration_manager(metaclass = Configuration_manager_meta):
	project_dir = os.path.realpath(os.path.dirname(__file__))
	config_path = os.path.join(project_dir, "..", "config/config.yaml")
	registry_path = os.path.join(project_dir, "..", "config/registry.yaml")
	env_var_pattern = re.compile('.*?\${(\w+)}.*?')

	def constructor_env_variables(self, loader, node):
		value = loader.construct_scalar(node)
		match = self.env_var_pattern.findall(value)

		if match:
			full_value = value
			for g in match:
				full_value = full_value.replace(
					f'${{{g}}}', os.environ.get(g, g)
				)
			return full_value
		return value
		
	def load_config(self) -> bool:
		logger.info(f"Opening config file in: {self.config_path}")

		loader = yaml.SafeLoader
		loader.add_implicit_resolver('', self.env_var_pattern, None)
		loader.add_constructor('', self.constructor_env_variables)

		with open(self.config_path) as config_file:
			try:
				self.config = yaml.load(config_file, Loader=loader)
				logger.info("Loaded")
			except yaml.YAMLError as error:
				logger.critical(f"Configuration file could not be safely loaded.\n\t{format(error)}")
		
		return True
	
	def load_registry(self) -> bool:
		logger.info(f"Opening registry file in: {self.registry_path}")

		if (not File_manager.exists(self.registry_path)):
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
	
	def load_aws_secrets(self) -> bool:
		aws = AWS(self.config["aws"]["access_key_id"], self.config["aws"]["secret_access_key"], self.config["aws"]["region"])
		aws.init_secret_manager()

		if (not self.config or self.config == None):
			return False
		
		if (self.config["sendgrid"]):
			self.config["sendgrid"] = dict()
			
			sendgrid = aws.get_secret("Sendgrid_API")

			if (sendgrid):
			self.config["sendgrid"]["api_key"] = sendgrid["Sendgrid_API_Key"]
			self.config["sendgrid"]["sender"] = sendgrid["Sendgrid_Sender"]
			else:
				self.config["sendgrid"] = False
		
		if (self.config["innova_monitor"]):
			self.config["innova_monitor"] = dict()
			
			innova_monitor = aws.get_secret("Innova_Monitor")

			if (not innova_monitor):
				return False
			
			self.config["innova_monitor"]["secret"] = innova_monitor["secret"]
			self.config["innova_monitor"]["url"] = innova_monitor["url"]
			

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
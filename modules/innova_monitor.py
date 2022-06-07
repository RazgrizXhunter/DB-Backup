import logging, requests
from modules.configuration_manager import Configuration_manager
from modules.file_manager import File_manager

logger = logging.getLogger("logger")

class Innova_monitor:
	def __init__(self) -> None:
		confmanager = Configuration_manager()
		self.file_manager = File_manager()

		self.instance = confmanager.config["instance"]

		self.session = requests.Session()
		self.session.headers = { "secret": self.config["secret"] }
		self.api_url = self.config["url"]

		self.machine = {
			"ip" : self.instance["ip"] if "ip" in self.instance else self.my_ip(),
			"name" : self.instance["name"] if "name" in self.instance else self.file_manager.get_hostname(),
			"total_space": self.file_manager.get_total_disk_space(),
			"warning_percentage": confmanager.config["custom_alerts"]["space_warning"],
			"critical_percentage": confmanager.config["custom_alerts"]["space_critical"]
		}
	
	def ping(self) -> bool:
		try:
			return True if self.session.get(self.api_url + "/ping").status_code == 200 else False # self.api_url + "/ping"
		except Exception as e:
			logger.error(e)
			return False
		
	def my_ip(self) -> str:
		return self.session.get("https://api.ipify.org").content.decode("utf8")

	def checkout(self) -> bool:
		logger.info("Sending data to Monitor")

		data = {
			"ip": self.machine["ip"],
			"name": self.machine["name"],
			"total_space": self.machine["total_space"],
			"free_space": self.file_manager.get_free_disk_space(),
			"warning_percentage": self.machine["warning_percentage"],
			"critical_percentage": self.machine["critical_percentage"]
		}

		try:
			response = self.session.post(self.api_url, data = data)

			if response.status_code == 200:
				logger.info("Done!")
				return True
			else:
				logger.error(f"Monitor responded with {response}")
				return False

		except Exception:
			logger.error("Could not post data to Monitor")
			return False


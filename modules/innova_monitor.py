import logging, requests
from datetime import datetime
from modules.configuration_manager import Configuration_manager
from modules.file_manager import File_manager
from modules.aws import AWS

logger = logging.getLogger("logger")

class Innova_monitor:
	def __init__(self) -> None:
		self.session = requests.Session()
		confmanager = Configuration_manager()
		aws = AWS()

		self.instance = confmanager.config["instance"]
		self.api_url = aws.get_secret("Innova_Monitor")["url"] if confmanager.config["innova_monitor"] else None;
		self.api_secret = aws.get_secret("Innova_Monitor")["secret"] if confmanager.config["innova_monitor"] else None;
		self.session.headers = { "secret": self.api_secret }

		self.machine = {
			"id" : self.my_id(),
			"name_tag" : self.my_nametag(),
			"ip" : self.instance["ip"] if "ip" in self.instance else self.my_ip(),
			"name" : self.instance["name"] if "name" in self.instance else File_manager.get_hostname(),
			"total_space": File_manager.get_total_disk_space(),
			"warning_percentage": confmanager.config["custom_alerts"]["space_warning"],
			"critical_percentage": confmanager.config["custom_alerts"]["space_critical"]
		}
	
	def ping(self) -> bool:
		try:
			return True if self.session.get(self.api_url + "/ping").status_code == 200 else False # self.api_url + "/ping"
		except Exception as e:
			logger.error(f"Could not ping Innova Monitor\n{e}")
			return False
		
	def my_ip(self) -> str:
		return self.session.get("https://api.ipify.org").content.decode("utf8")
	
	def my_id(self) -> str:
		try:
			return self.session.get("http://instance-data/latest/meta-data/instance-id").content.decode("utf8")
		except:
			return None

	def my_nametag(self) -> str:
		return self.session.get("http://instance-data/latest/meta-data/tags/instance/Name").content.decode("utf8")

	def checkout(self) -> bool:
		logger.info("Sending data to Monitor")
		now = datetime.now()

		data = {
			"id" : self.machine["id"],
			"name_tag" : self.machine["name_tag"],
			"ip" : self.machine["ip"],
			"name" : self.machine["name"],
			"last_updated" : now.strftime("%d/%m/%Y %H:%M:%S"),
			"total_space" : self.machine["total_space"],
			"free_space" : File_manager.get_free_disk_space(),
			"warning_percentage" : self.machine["warning_percentage"],
			"critical_percentage" : self.machine["critical_percentage"]
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


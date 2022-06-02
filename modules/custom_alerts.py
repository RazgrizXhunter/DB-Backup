import logging
from modules.configuration_manager import Configuration_manager
from modules.file_manager import File_manager

logger = logging.getLogger("logger")

class Custom_alerts:
	alerts = {}

	def __init__(self):
		self.confmanager = Configuration_manager()
		self.file_manager = File_manager()

		logger.debug("Loading custom alerts")

		if "custom_alerts" in self.confmanager.config:
			self.alerts = self.confmanager.config["custom_alerts"]

	def space_alert(self):
		if "space_critical" not in self.alerts:
			logger.warning("Can't raise an alert for free space without critical percentage!")
			return

		free = self.file_manager.get_free_disk_space()
		total = self.file_manager.get_total_disk_space()

		logger.info(f"Executing storage space check.\n\tFree space: {self.file_manager.to_human_readable_size(free)}\n\tTotal space: {self.file_manager.to_human_readable_size(total)}")

		critical_percentage = self.alerts["space_critical"]
		critical_level = round(total * (critical_percentage / 100))

		logger.debug(f"Critical storage level set on: {self.file_manager.to_human_readable_size(critical_level)}")

		if (free < critical_level):
			return True
		else:
			return False
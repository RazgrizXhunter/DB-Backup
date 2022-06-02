#!/usr/bin/env python
import os, logging
from modules.configuration_manager import Configuration_manager
from modules.backup_manager import Backup_manager
from modules.argument_manager import Argument_manager
from modules.innova_monitor import Innova_monitor

logger = logging.getLogger("logger")

if (__name__ == "__main__"):
	Argument_manager()

	project_dir = os.path.realpath(os.path.dirname(__file__))
	config_path = os.path.join(project_dir, "config/config.yaml")
	registry_path = os.path.join(project_dir, "config/registry.yaml")
	
	confmanager = Configuration_manager()
	confmanager.load_config(config_path)
	confmanager.load_registry(registry_path)

	backup_manager = Backup_manager()
	innova_monitor = Innova_monitor()

	for project in confmanager.config["projects"]:
		if "site" in project:
			key = project["site"]["path"]
			
			if (confmanager.has_entry(key)):
				entry = confmanager.get_entry(key)
			else:
				entry = confmanager.new_entry(key)
			
			frequency = project["site"]["backup_frequency"]
			
			if (backup_manager.backup_is_due(entry, frequency)):
				backup_manager.backup_site(project["site"], confmanager.config["backup"]["target_directory"])
				confmanager.update_entry(key)
			else:
				logger.info(f"Site files {key} backup is up-to-date.")
		
		if "schema" in project:
			key = project["schema"]["name"]
			
			if (confmanager.has_entry(key)):
				entry = confmanager.get_entry(key)
			else:
				entry = confmanager.new_entry(key)
			
			frequency = project["schema"]["backup_frequency"]
			
			if (backup_manager.backup_is_due(entry, frequency)):
				backup_manager.backup_database(project["schema"], confmanager.config["backup"]["target_directory"])
				confmanager.update_entry(key)
			else:
				logger.info(f"Schema {key} backup is up-to-date.")

	if (innova_monitor.ping()):
		innova_monitor.checkout()
	else:
		logger.warning("Innova Monitor unresponsive")
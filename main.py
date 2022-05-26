#!/usr/bin/env python

from configuration_manager import Configuration_manager
from backup_manager import Backup_manager
from argument_manager import Argument_manager

if (__name__ == "__main__"):
	Argument_manager()

	confmanager = Configuration_manager()
	confmanager.load_config("config.yaml")
	confmanager.load_registry("registry.yaml")

	backup_manager = Backup_manager()

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

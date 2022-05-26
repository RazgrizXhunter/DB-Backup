#!/usr/bin/env python

from backup_manager import Backup_manager
from configuration_manager import Configuration_manager
from argument_manager import Argument_manager

if (__name__ == "__main__"):
	Argument_manager()

	confmanager = Configuration_manager()
	confmanager.load_config("config.yaml")
	confmanager.load_registry("registry.yaml")

	backup_manager = Backup_manager()

	for project in confmanager.config["projects"]:
		if "site" in project:
			if (confmanager.has_entry(project["name"]["site"])):
				entry = confmanager.registry[project["name"]["site"]]
			else:
				entry = confmanager.new_entry(project["name"]["site"])
			
			frequency = project["site"]["backup_frequency"]
			
			if (backup_manager.backup_is_due(entry, frequency)):
				backup_manager.backup_site(project["site"], confmanager.config["backup"]["target_directory"])
		
		if "schema" in project:
			if (confmanager.has_entry(project["name"]["schema"])):
				entry = confmanager.registry[project["name"]["schema"]]
			else:
				entry = confmanager.new_entry(project["name"]["schema"])
			
			frequency = project["schema"]["backup_frequency"]
			
			if (backup_manager.backup_is_due(entry, frequency)):
				backup_manager.backup_database(project["schema"], confmanager.config["backup"]["target_directory"])

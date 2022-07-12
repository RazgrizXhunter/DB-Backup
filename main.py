#!/usr/bin/env python
import os, logging
from modules.configuration_manager import Configuration_manager
from modules.backup_manager import Backup_manager
from modules.argument_manager import Argument_manager

logger = logging.getLogger("logger")

def main():
	confmanager = Configuration_manager()
	confmanager.load_config()
	confmanager.load_registry()
	confmanager.load_aws_secrets()
	backup_manager = Backup_manager()
	Argument_manager()

	for project in confmanager.config["projects"]:
		project_name = list(project.keys())[0]

		if "site" in project:
			key = project["site"]["path"]
			
			if (confmanager.has_entry(key)):
				entry = confmanager.get_entry(key)
			else:
				entry = confmanager.new_entry(key)
			
			frequency = project["site"]["backup_frequency"]
			
			if (backup_manager.backup_is_due(entry, frequency)):
				success = backup_manager.backup_site(
					project_name = project_name,
					site_path = project["site"]["path"],
					target_directory = confmanager.config["backup"]["target_directory"],
					compress = project["site"]["compress"],
					preserve = project["site"]["preserve"]
				)
				
				if (success):
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
				success = backup_manager.backup_database(
					project_name = project_name,
					schema = project["schema"]["name"],
					target_directory = confmanager.config["backup"]["target_directory"],
					compress = project["schema"]["compress"],
					preserve = project["schema"]["preserve"]
				)

				if (success):
					confmanager.update_entry(key)
				
			else:
				logger.info(f"Schema {key} backup is up-to-date.")

if (__name__ == "__main__"):
	main()

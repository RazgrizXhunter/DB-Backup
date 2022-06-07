#!/usr/bin/env python
import os, logging
from modules.configuration_manager import Configuration_manager
from modules.backup_manager import Backup_manager
from modules.argument_manager import Argument_manager
from modules.aws import AWS

logger = logging.getLogger("logger")

def main():
	confmanager = load_config()
	Argument_manager()
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
				success = backup_manager.backup_site(project["site"], confmanager.config["backup"]["target_directory"])
				
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
				success = backup_manager.backup_database(project["schema"], confmanager.config["backup"]["target_directory"])

				if (success):
					confmanager.update_entry(key)
				
			else:
				logger.info(f"Schema {key} backup is up-to-date.")

def load_config():
	project_dir = os.path.realpath(os.path.dirname(__file__))
	config_path = os.path.join(project_dir, "config/config.yaml")
	registry_path = os.path.join(project_dir, "config/registry.yaml")
	
	confmanager = Configuration_manager()
	confmanager.load_config(config_path)
	confmanager.load_registry(registry_path)

	AWS(confmanager.config["aws"]["region"], confmanager.config["aws"]["access_key_id"], confmanager.config["aws"]["secret_access_key"])

	confmanager.load_aws_secrets()

	return confmanager

if (__name__ == "__main__"):
	main()

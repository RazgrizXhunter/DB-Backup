#!/usr/bin/env python
from datetime import datetime
import logging
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
            
            is_due = backup_manager.backup_is_due(entry, frequency)
            critical = project["site"]["critical"]

            if (critical): 
                should_backup = is_due

            else: 
                should_backup = is_due and datetime.now().hour == 0 # If it's not critical, only backup at 00:xx

            if (should_backup):
                success = backup_manager.backup_site(
                    project_name = project_name,
                    site_path = project["site"]["path"],
                    target_directory = confmanager.config["backup"]["target_directory"],
                    compress = project["site"]["compress"],
                    preserve = project["site"]["preserve"],
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

            is_due = backup_manager.backup_is_due(entry, frequency)
            critical = project["schema"]["critical"]

            if (critical): 
                should_backup = is_due

            else: 
                should_backup = is_due and datetime.now().hour == 0 # If it's not critical, only backup at 00:xx
            
            if (should_backup):
                try:
                    project_database = project["schema"]["database"]
                except KeyError:
                    logger.error(f"The project {project_name} has a schema but doesn't have a database configured")
                    continue

                database = confmanager.select_database(project_database)
                
                if (database == None):
                    logger.error(f"The project {project_name} has {project['schema']['database']} configured but it couldn't be found.")
                    continue

                success = backup_manager.backup_database(
                    database = database,
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

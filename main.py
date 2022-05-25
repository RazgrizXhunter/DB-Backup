#!/usr/bin/env python

import logging
from database_manager import Database_manager
from configuration_manager import Configuration_manager
from file_manager import File_manager
from argument_manager import Argument_manager
from aws import AWS

logger = logging.getLogger("logger")

if (__name__ == "__main__"):
	confmanager = Configuration_manager()
	confmanager.load_config("config.yaml")

	argmanager = Argument_manager()
	filemanager = File_manager()
	dbmanager = Database_manager(confmanager.config)

	aws = AWS()
	bucket = confmanager.config["bucket"]
	
	aws.init_s3(bucket["aws_access_key_id"], bucket["aws_secret_access_key"], bucket["name"])

	for project in confmanager.config["projects"]:

		if "site" in project:
			site_files = project["site"]
			logger.info(f"Now trying to backup files in \"{site_files['path']}\"")

			if (not filemanager.exists(site_files["path"])):
				logger.error("Provided file path doesn't exist")
				continue
			
			if (site_files["compress"]):
				free_disk_space = filemanager.get_free_disk_space()
				directory_size = filemanager.get_size(site_files["path"])
				logger.info(f"Free space: {filemanager.to_human_readable_size(free_disk_space)}, Site directory size: {filemanager.to_human_readable_size(directory_size)}")

				if (free_disk_space < directory_size):
					logger.critical("Not enough space to backup site files")
					continue

				compressed_site_backup_file_path = filemanager.compress(file_path=site_files["path"], remove_original=(not site_files["preserve"]))
			
				aws.s3_upload(compressed_site_backup_file_path)
			else:
				aws.s3_upload(site_files["path"])

		if "schema" in project:
			schema = project["schema"]
			logger.info(f"Now trying to backup schema \"{schema['name']}\"")

			free_disk_space = filemanager.get_free_disk_space()
			schema_size = dbmanager.get_schema_size(schema["name"])
			logger.info(f"Free space: {filemanager.to_human_readable_size(free_disk_space)}, Schema size: {filemanager.to_human_readable_size(schema_size)}")

			if (free_disk_space < schema_size):
				logger.critical("Not enough space to back up database")
				continue
			
			backup_file_path = dbmanager.dump(schema["name"])

			if (schema["compress"]):
				backup_file_path = filemanager.compress(file_path=backup_file_path, remove_original=(not schema["preserve"]))
			
			aws.s3_upload(backup_file_path)

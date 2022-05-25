#!/usr/bin/env python

import logging
from database_manager import Database_manager
from configuration_manager import Configuration_manager
from file_manager import File_manager
from argument_manager import Argument_manager
from aws import AWS

logger = logging.getLogger("logger")

if (__name__ == "__main__"):
	argmanager = Argument_manager()
	filemanager = File_manager()
	confmanager = Configuration_manager("config.yaml")
	dbmanager = Database_manager(confmanager.config)
	aws = AWS()

	for project in confmanager.config["projects"]:

		if "site" in project:
			# backup site directory
			pass

		if "schema" in project:
			schema = project["schema"]
			logger.debug(f"Now trying to backup schema \"{schema['name']}\"")

			free_disk_space = filemanager.get_free_disk_space()
			schema_size = dbmanager.get_schema_size(schema["name"])
			logger.info(f"Free space: {filemanager.to_human_readable_size(free_disk_space)}, Schema size: {filemanager.to_human_readable_size(schema_size)}")

			if (free_disk_space < schema_size):
				logger.critical("Not enough space to back up database")
				continue
			
			backup_file_path = dbmanager.dump(schema["name"])
			compressed_backup_file_path = filemanager.compress(file_path=backup_file_path, remove_original=True)

			aws.init_s3(confmanager.config["bucket"]["aws_access_key_id"], confmanager.config["bucket"]["aws_secret_access_key"], confmanager.config["bucket"]["name"])
			
			aws.s3_upload(compressed_backup_file_path)

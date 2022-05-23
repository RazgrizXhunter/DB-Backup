#!/usr/bin/env python

# a backup is not complete unless you make a copy of the binlogs along with it
# mysqldump doesn’t include routines and events in its output - you have to explicitly set --routines (-R) and --events (-E) flags
# if you want to take a consistent backup then things become tricky. As long as you use InnoDB only, you can use --single-transaction flag and you should be all set
# Mydumper/myloader

import logging
from backer import s3_backer
from filemanager import file_manager
from argument_manager import arg_manager
from aws import aws

logger = logging.getLogger("logger")

if (__name__ == "__main__"):
	args = arg_manager()
	fmanager = file_manager()

	aws = aws()

	backer = s3_backer()
	backer.load_config("config.yaml")

	for schema in backer.config["database"]["schemas"]:
		logger.debug(f"{schema['name']}")

		free_disk_space = fmanager.get_free_disk_space()
		schema_size = backer.get_schema_size(schema["name"])
		logger.info(f"Free space: {fmanager.to_human_readable_size(free_disk_space)}, Schema size: {fmanager.to_human_readable_size(schema_size)}")

		if (free_disk_space < schema_size):
			logger.critical("Not enough space to back up")
			continue
		
		backup_file_path = backer.dump(schema["name"])
		compressed_backup_file_path = fmanager.compress(file_path=backup_file_path, remove_original=True)

		aws.init_s3(backer.config["bucket"]["aws_access_key_id"], backer.config["bucket"]["aws_secret_access_key"], backer.config["bucket"]["name"])
		
		aws.s3_upload(compressed_backup_file_path)

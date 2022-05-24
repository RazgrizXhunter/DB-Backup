#!/usr/bin/env python

import logging
from backer import S3_backer
from file_manager import File_manager
from argument_manager import Argument_manager
from aws import AWS
from mailing import Mailer

logger = logging.getLogger("logger")

if (__name__ == "__main__"):
	argmanager = Argument_manager()
	fmanager = File_manager()
	backer = S3_backer()
	backer.load_config("config.yaml")

	mailer = Mailer(backer.config["sendgrid"]["api_key"])

	aws = AWS()

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

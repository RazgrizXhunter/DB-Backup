# a backup is not complete unless you make a copy of the binlogs along with it
# mysqldump doesn’t include routines and events in its output - you have to explicitly set --routines (-R) and --events (-E) flags
# if you want to take a consistent backup then things become tricky. As long as you use InnoDB only, you can use --single-transaction flag and you should be all set
# Mydumper/myloader

# import boto3
import logging
from backer import s3_backer
from filemanager import file_manager
from argument_manager import arg_manager
from aws import aws

logger = logging.getLogger("logger")

if (__name__ == "__main__"):
	args = arg_manager()
	backer = s3_backer()
	backer.load_config("config.yaml")

	fmanager = file_manager()

	for schema in backer.config["database"]["schemas"]:
		logger.debug(f"{schema['name']}")

		if (not fmanager.exists(schema["path"])):
			logger.warning("Specified directory doesn't exists. Skipping...")
			continue

		free_disk_space = fmanager.get_free_disk_space()
		schema_size = fmanager.get_size(schema["path"])
		logger.info(f"Free space: {free_disk_space}, Schema size: {schema_size}")

		if (free_disk_space < schema_size):
			logger.critical("Not enough space to back up")
			continue
		
		backup_file_path = backer.dump(schema["name"])
		fmanager.compress(file_path=backup_file_path)

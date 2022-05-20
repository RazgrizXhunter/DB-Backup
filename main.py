# a backup is not complete unless you make a copy of the binlogs along with it
# mysqldump doesn’t include routines and events in its output - you have to explicitly set --routines (-R) and --events (-E) flags
# if you want to take a consistent backup then things become tricky. As long as you use InnoDB only, you can use --single-transaction flag and you should be all set
# Mydumper/myloader

# import boto3
from backer import s3_backer
from filemanager import file_manager

if (__name__ == "__main__"):
	backer = s3_backer()
	backer.load_config("config.yaml")

	fmanager = file_manager()

	for schema in backer.config["database"]["schemas"]:
		free_disk_space = fmanager.get_free_disk_space()
		schema_size = fmanager.get_size(schema["path"])

		if (not schema_size):
			print("Specified directory doesn't exists. Skipping...")
			pass
		elif (free_disk_space > schema_size):
			backup_file_path = backer.dump(schema["name"])
			fmanager.compress(file_path=backup_file_path)
		else:
			print("Not enough space to back up")
			pass

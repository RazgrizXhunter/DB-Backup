# a backup is not complete unless you make a copy of the binlogs along with it
# mysqldump doesn’t include routines and events in its output - you have to explicitly set --routines (-R) and --events (-E) flags
# if you want to take a consistent backup then things become tricky. As long as you use InnoDB only, you can use --single-transaction flag and you should be all set
# Mydumper/myloader

# import boto3
import psutil, math
from backer import s3_backer

if (__name__ == "__main__"):
	backer = s3_backer()
	backer.load_config("config.yaml")
	# Check disk space before dumping, it should be equal or greater than the database to dump
	free_disk_space = round(psutil.disk_usage("/").free / (2 ** 30), 3)
	print(free_disk_space)
	backup_file_path = backer.dump()
	backer.compress(backup_file_path, remove_original=True)

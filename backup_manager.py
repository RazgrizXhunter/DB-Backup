import logging, datetime
from configuration_manager import Configuration_manager
from file_manager import File_manager
from database_manager import Database_manager
from aws import AWS

logger = logging.getLogger("logger")

class Backup_manager:
	confmanager = Configuration_manager()
	file_manager = File_manager()
	dbmanager = Database_manager(confmanager.config)
	aws = AWS()
	
	today = None

	def __init__(self):
		self.today = datetime.datetime.today()
		bucket = self.confmanager.config["bucket"]
		self.aws.init_s3(bucket["aws_access_key_id"], bucket["aws_secret_access_key"], bucket["name"])

	def backup_is_due(self, entry, frequency):
		last_backup = self.confmanager.registry[entry]

		if (not last_backup):
			return True
		
		backup_due = last_backup + datetime.timedelta(days=frequency)

		if (backup_due <= self.today):
			return True
		else:
			return False

	def backup_site(self, site_files, target_directory, aws):
		logger.info(f"Now trying to backup files in \"{site_files['path']}\"")

		if (not self.file_manager.exists(site_files["path"])):
			logger.error("Provided file path doesn't exist")
			return
		
		if (site_files["compress"]):
			directory_size = self.file_manager.get_size(site_files["path"])

			if (not self.file_manager.has_enough_space(directory_size)):
				logger.error("Not enough space to backup site files")
				return

			compressed_site_backup_file_path = self.file_manager.compress(file_path=site_files["path"], target_directory=target_directory) # NEVER REMOVE ORIGINAL, IT'D DELETE THE SITE!

			aws.s3_upload(compressed_site_backup_file_path)

			if (not site_files["preserve"]):
				self.file_manager.delete(compressed_site_backup_file_path)
		
		else:
			aws.s3_upload(site_files["path"])

	def backup_database(self, schema, target_directory, aws):
		logger.info(f"Now trying to backup schema \"{schema['name']}\"")
		schema_size = self.database_manager.get_schema_size(schema["name"])

		if (not self.file_manager.has_enough_space(schema_size)):
			logger.error("Not enough space to back up database")
			return
		
		backup_file_path = self.database_manager.dump_schema(schema["name"])

		if (schema["compress"]):
			backup_file_path = self.file_manager.compress(file_path=backup_file_path, target_directory=target_directory, remove_original=(not schema["preserve"]))
		
		aws.s3_upload(backup_file_path)

		if (not schema["preserve"]):
			self.file_manager.delete(backup_file_path)
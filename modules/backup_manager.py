import logging, datetime
from modules.configuration_manager import Configuration_manager
from modules.file_manager import File_manager
from modules.database_manager import Database_manager
from modules.aws import AWS

logger = logging.getLogger("logger")

class Backup_manager:
	today = None

	def __init__(self):
		self.confmanager = Configuration_manager()
		self.dbmanager = Database_manager()
		self.aws = AWS()
		
		self.aws.init_s3(self.confmanager.config["bucket"]["name"])

	def backup_is_due(self, entry, frequency):

		if (not entry):
			return True
		
		backup_due = entry + datetime.timedelta(hours=frequency)

		if (backup_due <= datetime.datetime.today()):
			return True
		else:
			return False

	def backup_site(self, site_files, target_directory):
		has_backed_up = False

		logger.info(f"Now trying to backup files in \"{site_files['path']}\"")

		if (not File_manager.exists(site_files["path"])):
			logger.error("Provided file path doesn't exist")
			return
		
		if (site_files["compress"]):
			directory_size = File_manager.get_size(site_files["path"])

			if (not File_manager.has_enough_space(directory_size)):
				logger.error("Not enough space to backup site files")
				return

			compressed_site_backup_file_path = File_manager.compress(file_path=site_files["path"], target_directory=target_directory) # NEVER REMOVE ORIGINAL, IT'D DELETE THE SITE!

			has_backed_up = self.aws.s3_upload(compressed_site_backup_file_path)

			if (not site_files["preserve"]):
				File_manager.delete(compressed_site_backup_file_path)
		
		else:
			has_backed_up = self.aws.s3_upload(site_files["path"])
		
		return has_backed_up

	def backup_database(self, schema, target_directory):
		has_backed_up = False

		logger.info(f"Now trying to backup schema \"{schema['name']}\"")
		schema_size = self.dbmanager.get_schema_size(schema["name"])

		if (not File_manager.has_enough_space(schema_size)):
			logger.error("Not enough space to back up database")
			return
		
		backup_file_path = self.dbmanager.dump_schema(schema["name"])

		if (schema["compress"]):
			backup_file_path = File_manager.compress(file_path=backup_file_path, target_directory=target_directory, remove_original=(not schema["preserve"]))
		
		has_backed_up = self.aws.s3_upload(backup_file_path)

		if (not schema["preserve"]):
			File_manager.delete(backup_file_path)
		
		return has_backed_up
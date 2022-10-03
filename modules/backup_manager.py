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
		tolerance = 0.5 # In hours, arbitrary. Since backups aren't actually made at the exact same time each time, it can skip one if it's early a couple of seconds.

		if (not entry):
			return True
		
		backup_due = entry + datetime.timedelta(hours=frequency - tolerance)

		if (backup_due <= datetime.datetime.today()):
			return True
		else:
			return False

	def backup_site(self, project_name: str, site_path: str, target_directory: str, compress: bool, preserve: bool) -> bool:
		has_backed_up = False

		logger.info(f"Now trying to backup files in \"{site_path}\"")

		if (not File_manager.exists(site_path)):
			logger.error("Provided file path doesn't exist.")
			return False
		
		if (not File_manager.exists(target_directory)):
			try:
				File_manager.create_directory(target_directory)
			except Exception as e:
				logger.critical(f"Could not create backup directory.")
				return False
		
		if (compress):
			directory_size = File_manager.get_size(site_path)

			if (not File_manager.has_enough_space(directory_size)):
				logger.error("Not enough space to backup site files")
				return False

			compressed_site_backup_file_path = File_manager.compress(
				file_path = site_path,
				target_directory = target_directory,
				project_name = project_name
			) # NEVER REMOVE ORIGINAL, IT'D DELETE THE SITE!

			has_backed_up = self.aws.s3_upload(
				file_path = compressed_site_backup_file_path,
				subfolder = project_name
			)

			if (not preserve):
				File_manager.delete(compressed_site_backup_file_path)
		
		else:
			has_backed_up = self.aws.s3_upload(
				file_path = site_path,
				subfolder = project_name
			)

		return has_backed_up

	def backup_database(self, project_name: str, schema: str, target_directory: str, compress: bool, preserve: bool) -> bool:
		has_backed_up = False

		logger.info(f"Now trying to backup schema \"{schema}\"")
		schema_size = self.dbmanager.get_schema_size(schema)

		if (not File_manager.has_enough_space(schema_size)):
			logger.error("Not enough space to back up database")
			return False
		
		if (not File_manager.exists(target_directory)):
			try:
				File_manager.create_directory(target_directory)
			except Exception as e:
				logger.critical(f"Could not create backup directory.")
				return False
		
		backup_file_path = self.dbmanager.dump_schema(schema)

		if (compress):
			backup_file_path = File_manager.compress(
				file_path = backup_file_path,
				target_directory = target_directory,
				remove_original = (not preserve)
			)
		
		has_backed_up = self.aws.s3_upload(
			file_path = backup_file_path,
			subfolder = project_name
		)

		if (not preserve):
			File_manager.delete(backup_file_path)
		
		return has_backed_up
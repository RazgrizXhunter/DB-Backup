import sys, logging
import boto3
from modules.file_manager import File_manager

logger = logging.getLogger("logger")

class AWS:

	def __init__(self):
		self.s3 = None
		self.session = None
		self.bucket = None
	
	def init_s3(self, key: str, secret: str, bucket: str) -> bool:
		try:
			self.session = boto3.Session(
				aws_access_key_id=key,
				aws_secret_access_key=secret
			)
			
			self.s3 = self.session.resource("s3")

			self.bucket = self.s3.Bucket(bucket)

			return True
		except Exception as e:
			logger.critical(f"AWS S3 service could not be initialized\n\t{e}")
	
	def s3_upload(self, file_path: str, file_name: str = "") -> bool:
		fmanager = File_manager()

		logger.info("Preparing to upload file to S3 bucket")
		logger.debug(f"File: {file_path}")

		if (not self.s3):
			logger.critical("S3 session uninitialized")

		if (not fmanager.exists(file_path)):
			logger.error(f"Failed to upload file {file_path}. The file doesn't exist")
			return False
		
		if (not file_name): file_name = fmanager.get_name(file_path)
		
		try:
			self.bucket.upload_file(file_path, fmanager.get_name(file_path))
		except Exception as e:
			logger.error(f"Failed to upload file.\n\t{e}")
		
		logger.info("File uploaded succesfully")

		return True
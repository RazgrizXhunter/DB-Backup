import sys, logging
import boto3
from filemanager import file_manager as fmanager

logger = logging.getLogger("logger")

class aws():
	# s3 = None

	# def __init__(self):
	
	def init_s3(self, credentials: dict) -> bool:
		try:
			self.session = boto3.session(
				aws_access_key_id=credentials["key"],
				aws_secret_access_key=credentials["secret"]
			)
			self.s3 = boto3.resource("s3")

			return True
		except Exception as e:
			logger.error(e)
			sys.exit()
	
	def s3_upload(self, file_path: str, bucket_name: str, file_name: str = "") -> bool:
		logger.info(f"Preparing to upload file to S3 bucket: {bucket_name}")

		if (not self.s3):
			logger.error("S3 session uninitialized")

		if (not fmanager.exists(file_path)):
			logger.error(f"Failed to upload file {file_path}. The file doesn't exist")
			return False
		
		if (not file_name): file_name = fmanager.get_name(file_path)
		
		try:
			self.s3.bucket(bucket_name).upload_file(file_path, fmanager.get_name(file_path))
		except Exception as e:
			logger.error(e)

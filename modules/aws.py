import sys, logging, base64
import boto3
from modules.file_manager import File_manager
from botocore.exceptions import ClientError

logger = logging.getLogger("logger")

class AWS:

	def __init__(self):
		self.s3 = None
		self.secret_manager = None
		self.session = None
		self.bucket = None
		self.region_name = "us-east-1"
	
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
			return False
		
		logger.info("File uploaded succesfully")

		return True

	
	def get_secret(self, secret_name: str) -> str:
		logger.debug(f"AWS Secret Manager\nGetting Secret: {secret_name}")

		secret_name = "Sendgrid_API"

		self.secret_manager = self.session.client(
			service_name = "secretsmanager",
			region_name = self.region_name
		)

		try:
			get_secret_value_response = self.secret_manager.get_secret_value(
				SecretId = secret_name
			)
		except ClientError as error:
			if error.response["Error"]["Code"] == "DecryptionFailureException":
				logger.error("Secrets Manager can't decrypt the protected secret text using the provided KMS key")
				return False

			elif error.response["Error"]["Code"] == "InternalServiceErrorException":
				logger.error("An error occurred on the server side")
				return False

			elif error.response["Error"]["Code"] == "InvalidParameterException":
				logger.error("You provided an invalid value for a parameter")
				return False

			elif error.response["Error"]["Code"] == "InvalidRequestException":
				logger.error("You provided a parameter value that is not valid for the current state of the resource")
				return False

			elif error.response["Error"]["Code"] == "ResourceNotFoundException":
				logger.error("We can't find the resource that you asked for")
				return False
		else:
			logger.debug("Decrypting secret using the associated KMS key")

			if "SecretString" in get_secret_value_response:
				secret = get_secret_value_response["SecretString"]
			else:
				secret = base64.b64decode(get_secret_value_response["SecretBinary"])
	
		return secret

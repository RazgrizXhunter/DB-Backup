import logging, base64, json
import boto3
from botocore.exceptions import ClientError
from modules.file_manager import File_manager

logger = logging.getLogger("logger")

class AWS_meta(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			instance = super().__call__(*args, **kwargs)
			cls._instances[cls] = instance
		return cls._instances[cls]

class AWS(metaclass = AWS_meta):
	def __init__(self, id: str, key: str, region: str):
		self.s3 = None
		self.bucket = None
		self.secret_manager = None
		
		self.session = boto3.Session(
			aws_access_key_id = id,
			aws_secret_access_key = key
		)

		self.region_name = region
	
	def init_s3(self, bucket: str) -> bool:
		logger.debug(f"Initializing AWS' S3")

		try:
			self.s3 = self.session.resource("s3")
			self.bucket = self.s3.Bucket(bucket)
		except Exception as e:
			logger.critical(f"There was an error while initializing AWS' S3.\n\t{e}")
			return False

		return True

	def init_secret_manager(self) -> bool:
		logger.debug(f"Initializing AWS' Secret Manager")

		try:
			self.secret_manager = self.session.client(
				service_name = "secretsmanager",
				region_name = self.region_name
			)
		except Exception as e:
			logger.warning(f"There was an error while initializing AWS' Secret Manager.\n\t{e}")
			return False
		
		return True
	
	def s3_upload(self, file_path: str, file_name: str = "") -> bool:
		logger.info("Preparing to upload file to S3 bucket")
		logger.debug(f"File: {file_path}")

		if (not self.s3):
			logger.critical("S3 session uninitialized")

		if (not File_manager.exists(file_path)):
			logger.error(f"Failed to upload file {file_path}. The file doesn't exist")
			return False
		
		if (not file_name): file_name = File_manager.get_name(file_path)
		
		try:
			self.bucket.upload_file(file_path, file_name)
		except Exception as e:
			logger.error(f"Failed to upload file.\n\t{e}")
			return False
		
		logger.info("File uploaded succesfully")

		return True
	
	def get_secret(self, secret_name: str) -> dict:
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

		return json.loads(secret)

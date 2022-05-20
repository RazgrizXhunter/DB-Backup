import sys
import boto3
from ast import excepthandler
from filemanager import file_manager as fmanager

class aws():
	s3 = None

	def __init__(self):
		try:
			self.s3 = boto3.resource("s3")
		except Exception as e:
			print(e)
			sys.exit()
	
	def upload(self, file_path, bucket_name):
		if (not fmanager.exists(file_path)):
			print(f"Failed to upload file {file_path}. The file doesn't exist")
		
		with open(file_path) as file:
			try:
				self.s3.bucket(bucket_name).put_object(fmanager.get_name(file_path), file)
			except Exception as e:
				print(e)

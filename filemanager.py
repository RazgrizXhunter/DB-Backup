import os, time, psutil, logging
import gzip, zipfile, tarfile

logger = logging.getLogger("logger")

class file_manager:

	# def __init__(self):

	def compress(self, file_path, method="zip", remove_original=False):
		logger.info("Attempting compression...")

		if (method not in ["tar", "gz", "zip"]):
			logger.warning("Invalid compression method.")
			return False
		
		absolute_file_path = os.path.realpath(os.path.dirname(__file__))

		if (file_path[0] == "~"):
			absolute_file_path = os.path.join(absolute_file_path, file_path[1:])
		elif (file_path[0] == "/"):
			absolute_file_path = file_path
		else:
			absolute_file_path = os.path.join(absolute_file_path, file_path)
		
		if (not os.path.exists(absolute_file_path)):
			logger.error("Provided path doesn't exist")
			return False
		
		match (method):
			case "tar":
				tarfile.open(absolute_file_path, mode="w")
				
			case "gz":
				tarfile.open(absolute_file_path, mode="x:gz")

			case "zip":
				zip_filename = absolute_file_path.split(".")[0] + ".zip"
				
				try:
					with zipfile.ZipFile(zip_filename, mode="x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as compressed_file:
						compressed_file.write(absolute_file_path, self.get_name(absolute_file_path))

				except FileExistsError as e:
					logger.warning("Target file already exists")

				except Exception as e:
					logger.error(e)
		
		logger.info("Compression done")

		if (remove_original):
			logger.info("Deleting origin file")
			try:
				os.remove(absolute_file_path)
			except Exception as e:
				logger.error(e)
		
		return self.get_directory(absolute_file_path) + zip_filename
	
	def created_on(self, file_path):
		return time.ctime(os.path.getmtime(file_path))
	
	def get_free_disk_space(self):
		return round(psutil.disk_usage("/").free / (2 ** 30), 3)
	
	def exists(self, path):
		return os.path.exists(path)

	def get_size(self, path):		
		size = 0

		with os.scandir(path) as sd:
			for entry in sd:
				if entry.is_file():
					size += entry.stat().st_size
				elif entry.is_dir():
					size += self.get_size(entry.path)
		
		return round(size / (2 ** 30), 3)
 
	def get_name(self, path):
		return os.path.basename(path)
	
	def get_directory(self, path):
		return os.path.dirname(path)
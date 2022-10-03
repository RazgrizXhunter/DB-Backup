import os, time, psutil, logging, math, socket
import zipfile

logger = logging.getLogger("logger")

class File_manager:
	@staticmethod
	def compress(file_path, target_directory, project_name: str = None, method = "zip", remove_original = False):
		logger.info("Attempting compression...")

		if (method not in ["zip"]):
			logger.error("Invalid compression method.")
			return False
		
		absolute_file_path = File_manager.absolutize_path(file_path)

		if (not os.path.exists(absolute_file_path)):
			logger.error("Provided path doesn't exist")
			return False
		
		if (method == "zip"): # match - not supported by python 3.9 or less
			filename = project_name if not project_name == None else File_manager.get_name(absolute_file_path).split(".")[0]
			zip_filename = os.path.join(target_directory, filename.replace(" ", "_") + "_" + time.strftime('%Y-%m-%d_%H-%M-%S') + ".zip")
			
			try:
				logger.info(f"Compressing in: {zip_filename}")
				with zipfile.ZipFile(zip_filename, mode="x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as compressed_file:
					if (os.path.isdir(absolute_file_path)):
						File_manager.zipdir(absolute_file_path, compressed_file)
					else:
						compressed_file.write(absolute_file_path, File_manager.get_name(absolute_file_path))

			except FileExistsError as e:
				logger.warning("Target file already exists")

			except Exception as e:
				logger.error(f"File could not be compressed.\n\t{e}")
		else:
			logger.error("Compression method not supported")
		
		logger.info("Compression done")

		if (remove_original):
			File_manager.delete(absolute_file_path)
		
		return zip_filename
	
	@staticmethod
	def zipdir(path, zipfile_handle):
		for root, dirs, files in os.walk(path):
			for file in files:
				zipfile_handle.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
	
	@staticmethod
	def absolutize_path(path):
		absolute_file_path = os.path.realpath(os.path.dirname(__file__))

		if (path[0] == "~"):
			absolute_file_path = os.path.join(absolute_file_path, path[1:])
		elif (path[0] == "/"):
			absolute_file_path = path
		else:
			absolute_file_path = os.path.join(absolute_file_path, path)
		
		return absolute_file_path if absolute_file_path[len(absolute_file_path)-1] != "/" else absolute_file_path[:-1]
	
	@staticmethod
	def delete(path):
		logger.warning(f"Deleting {path}")
		try:
			os.remove(path)
		except Exception as e:
			logger.error(f"Could not complete deletion.\n\t{e}")
	
	@staticmethod
	def created_on(file_path):
		return time.ctime(os.path.getmtime(file_path))
	
	@staticmethod
	def get_free_disk_space():
		return psutil.disk_usage("/").free
	
	@staticmethod
	def get_total_disk_space():
		return psutil.disk_usage("/").total
	
	@staticmethod
	def exists(path):
		return os.path.exists(path)

	@staticmethod
	def create_directory(path: str):
		try:
			os.makedirs(path, exist_ok = True)
			return True
		except Exception as e:
			logger.error(f"Could not create directory {path}")
			return False

	@staticmethod
	def get_size(path):
		total_size = 0
		for dirpath, dirnames, filenames in os.walk(path):
			for f in filenames:
				fp = os.path.join(dirpath, f)
				# skip if it is symbolic link
				if not os.path.islink(fp):
					total_size += os.path.getsize(fp)

		return total_size
 
	@staticmethod
	def get_name(path):
		return os.path.basename(path)
	
	@staticmethod
	def get_directory(path):
		return os.path.dirname(path)
	
	@staticmethod
	def to_human_readable_size(size_bytes):
		if size_bytes == 0: return "0B"
		
		size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

		i = int(math.floor(math.log(size_bytes, 1024)))

		p = math.pow(1024, i)
		s = round(size_bytes / p, 2)
		return "%s %s" % (s, size_name[i])
	
	@staticmethod
	def has_enough_space(size):
		free_disk_space = File_manager.get_free_disk_space()
		
		logger.info(f"Free space: {File_manager.to_human_readable_size(free_disk_space)}, Files size: {File_manager.to_human_readable_size(size)}")

		if (free_disk_space >= size):
			return True

		return False
	
	@staticmethod
	def get_hostname():
		return socket.gethostname()
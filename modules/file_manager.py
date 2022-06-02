import os, time, psutil, logging, math, socket
import gzip, zipfile, tarfile

logger = logging.getLogger("logger")

class File_manager:

	def compress(self, file_path, target_directory, method="zip", remove_original=False):
		logger.info("Attempting compression...")

		if (method not in ["zip"]):
			logger.error("Invalid compression method.")
			return False
		
		absolute_file_path = self.absolutize_path(file_path)

		if (not os.path.exists(absolute_file_path)):
			logger.error("Provided path doesn't exist")
			return False
		
		if (method == "zip"): # match - not supported by python 3.9 or less
			zip_filename = os.path.join(target_directory, self.get_name(absolute_file_path).split(".")[0].replace(" ", "_") + ".zip")
			
			try:
				logger.info(f"Compressing in: {zip_filename}")
				with zipfile.ZipFile(zip_filename, mode="x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as compressed_file:
					if (os.path.isdir(absolute_file_path)):
						self.zipdir(absolute_file_path, compressed_file)
					else:
						compressed_file.write(absolute_file_path, self.get_name(absolute_file_path))

			except FileExistsError as e:
				logger.warning("Target file already exists")

			except Exception as e:
				logger.error(f"File could not be compressed.\n\t{e}")
		else:
			logger.error("Compression method not supported")
		
		logger.info("Compression done")

		if (remove_original):
			self.delete(absolute_file_path)
		
		return zip_filename
	
	def zipdir(self, path, zipfile_handle):
		for root, dirs, files in os.walk(path):
			for file in files:
				zipfile_handle.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
	
	def absolutize_path(self, path):
		absolute_file_path = os.path.realpath(os.path.dirname(__file__))

		if (path[0] == "~"):
			absolute_file_path = os.path.join(absolute_file_path, path[1:])
		elif (path[0] == "/"):
			absolute_file_path = path
		else:
			absolute_file_path = os.path.join(absolute_file_path, path)
		
		return absolute_file_path if absolute_file_path[len(absolute_file_path)-1] != "/" else absolute_file_path[:-1]
	
	def delete(self, path):
		logger.warning(f"Deleting {path}")
		try:
			os.remove(path)
		except Exception as e:
			logger.error(f"Could not complete deletion.\n\t{e}")
	
	def created_on(self, file_path):
		return time.ctime(os.path.getmtime(file_path))
	
	def get_free_disk_space(self):
		return psutil.disk_usage("/").free
	
	def get_total_disk_space(self):
		return psutil.disk_usage("/").total
	
	def get_hostname(self):
		return socket.gethostname()
	
	def exists(self, path):
		return os.path.exists(path)

	def get_size(self, path):
		total_size = 0
		for dirpath, dirnames, filenames in os.walk(path):
			for f in filenames:
				fp = os.path.join(dirpath, f)
				# skip if it is symbolic link
				if not os.path.islink(fp):
					total_size += os.path.getsize(fp)

		return total_size
 
	def get_name(self, path):
		return os.path.basename(path)
	
	def get_directory(self, path):
		return os.path.dirname(path)
	
	def to_human_readable_size(self, size_bytes):
		if size_bytes == 0: return "0B"
		
		size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

		i = int(math.floor(math.log(size_bytes, 1024)))

		p = math.pow(1024, i)
		s = round(size_bytes / p, 2)
		return "%s %s" % (s, size_name[i])
	
	def has_enough_space(self, size):
		free_disk_space = self.get_free_disk_space()
		
		logger.info(f"Free space: {self.to_human_readable_size(free_disk_space)}, Files size: {self.to_human_readable_size(size)}")

		if (free_disk_space >= size):
			return True

		return False
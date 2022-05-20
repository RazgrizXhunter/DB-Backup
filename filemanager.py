import os, time, psutil
import gzip, zipfile, tarfile

class file_manager:

	# def __init__(self):

	def compress(self, file_path, method="zip", remove_original=False):
		print("Attempting compression...")

		if (method not in ["tar", "gz", "zip"]):
			print("Invalid compression method.")
			return False
		
		absolute_file_path = os.path.realpath(os.path.dirname(__file__))

		if (file_path[0] == "~"):
			absolute_file_path = os.path.join(absolute_file_path, file_path[1:])
		elif (file_path[0] == "/"):
			absolute_file_path = file_path
		else:
			absolute_file_path = os.path.join(absolute_file_path, file_path)
		
		if (not os.path.exists(absolute_file_path)):
			print("Provided path doesn't exist")
			return False
		
		match method:
			case "tar":
				tarfile.open(absolute_file_path, mode="w")
				
			case "gz":
				tarfile.open(absolute_file_path, mode="x:gz")

			case "zip":
				zip_filename = absolute_file_path.split(".")[0] + ".zip"
				
				try:
					with zipfile.ZipFile(zip_filename, mode="x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as compressed_file:
						compressed_file.write(absolute_file_path, os.path.basename(absolute_file_path))

				except FileExistsError as e:
					print("Target file already exists")

				except Exception as e:
					print(e)
		
		print("Compression done")

		if (remove_original):
			print("Deleting origin file")
			try:
				os.remove(absolute_file_path)
			except Exception as e:
				print(e)
		
		return True
	
	def created_on(self, file_path):
		return time.ctime(os.path.getmtime(file_path))
	
	def get_free_disk_space(self):
		return round(psutil.disk_usage("/").free / (2 ** 30), 3)
	
	def get_size(self, path):
		if (not os.path.exists(path)):
			return False
		
		return round(psutil.disk_usage(path).free / (2 ** 30), 3)
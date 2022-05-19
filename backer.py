import sys, os, subprocess, time, yaml
import gzip, zipfile, tarfile

class s3_backer:
	config = None

	# def __init__(self):

	def load_config(self, filename):
		project_dir = os.path.realpath(os.path.dirname(__file__))
		config_file_path = os.path.join(project_dir, filename)

		print(f"Opening config file in: {config_file_path}")

		with open(config_file_path) as f:
			try:
				self.config = yaml.safe_load(f)
				print("Loaded")
			except yaml.YAMLError as error:
				print(format(error))
				sys.exit()
	
	def dump(self, extension="sql"):
		print(f"Attempting dump of database: {self.config['database']['name']}")

		if (self.config == None):
			return print("You need to load the config file first!")
		
		if (not os.path.isdir(self.config["backup"]["target_directory"])):
			print("Specified target directory doesn't exist. Creating...")
			try:
				os.mkdir(self.config["backup"]["target_directory"])
			except Exception as e:
				print("Directory could not be created")
				print(e)
				sys.exit()
		
		file_path = "{target_directory}/backup_{database_name}_{timestamp}.{extension}".format(
			target_directory = self.config["backup"]["target_directory"],
			database_name = self.config["database"]["name"],
			timestamp = time.strftime('%Y-%m-%d_%H-%M-%S'),
			extension = extension
		)
		
		command = "mysqldump -u{user} -p\'{password}\' {database_name}".format(
			user = self.config["database"]["user"],
			password = self.config["database"]["password"],
			database_name = self.config["database"]["name"],
			file_path = file_path.replace(" ", "\ ")
		)

		print(f"dumping on {file_path}")

		try:
			dump = subprocess.run(command, capture_output=True, shell=True)
			print("Dump complete!")
		except Exception as e:
			print(e)
			sys.exit()
		
		with open(file_path, "w") as file:
			file.write(dump.stdout.decode("utf-8"))
			file.close()
		
		return file_path
	
	def weight(self):
		statement = """
					SELECT table_schema \"DB Name\",
					ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) "DB Size in MB" 
					FROM information_schema.tables 
					GROUP BY table_schema;
					"""
		
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
				pass
				
			case "gz":
				tarfile.open(absolute_file_path, mode="x:gz")
				pass

			case "zip":
				zip_filename = absolute_file_path.split(".")[0] + ".zip"
				
				try:
					with zipfile.ZipFile(zip_filename, mode="x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as compressed_file:
						compressed_file.write(absolute_file_path, os.path.basename(absolute_file_path))

				except FileExistsError as e:
					print("Target file already exists")

				except Exception as e:
					print(e)
				
				pass
		
		print("Compression done")

		if (remove_original):
			print("Deleting origin file")
			try:
				os.remove(absolute_file_path)
			except Exception as e:
				print(e)
		
		return True


import argparse, sys, logging
from modules.error_handler import Error_handler

logger = logging.getLogger("logger")

class Argument_manager:
	args = None

	def __init__(self):
		parser = argparse.ArgumentParser(
			description="Utility tool to backup MySQL databases in AWS' S3 with Boto3",
			formatter_class=argparse.RawTextHelpFormatter
		)

		verbosity = parser.add_argument_group(
			title="Logging levels",
			description=
			"Select the logging level.\n"
			"\tCRITICAL: 50\n"
			"\tERROR: 40\n"
			"\tWARNING: 30 [Default]\n"
			"\tINFO: 20\n"
			"\tDEBUG: 10"
		)
		verbosity_exclusive = verbosity.add_mutually_exclusive_group()
		verbosity_exclusive.add_argument("-s", "--silent", action="store_true", help="Show levels 40+.")
		verbosity_exclusive.add_argument("-v", "--verbose", action="store_true", help="Show levels 20+.")
		verbosity_exclusive.add_argument("-d", "--debug", action="store_true", help="Show levels 10+.")
		
		self.args = parser.parse_args()

		params = self.get_params()

		logger.setLevel(logging.DEBUG)

		file = logging.FileHandler("backup.log")
		temporary_file = logging.FileHandler("backup.log.tmp")
		console = logging.StreamHandler()

		format = "%(levelname)s - %(asctime)s:\n\t%(message)s"
		formatter = logging.Formatter(format)

		file.setFormatter(formatter)
		file.setLevel(logging.DEBUG)
		
		temporary_file.setFormatter(formatter)
		temporary_file.setLevel(logging.DEBUG)

		console.setFormatter(CustomFormatter(format))

		if params["silent"]:
			console.setLevel(logging.CRITICAL)
		elif params["verbose"]:
			console.setLevel(logging.INFO)
		elif params["debug"]:
			console.setLevel(logging.DEBUG)
		else:
			console.setLevel(logging.WARNING)
		
		logger.addHandler(file)
		logger.addHandler(temporary_file)
		logger.addHandler(console)
		logger.addHandler(Error_handler())
	
	def get_params(self):
		return vars(self.args)

class CustomFormatter(logging.Formatter):
    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
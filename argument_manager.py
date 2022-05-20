import argparse, sys, logging

logger = logging.getLogger("logger")

class arg_manager():
	args = None

	def __init__(self):
		parser = argparse.ArgumentParser(
			description="Utility tool to backup MySQL databases in AWS with Boto3",
			formatter_class=argparse.ArgumentDefaultsHelpFormatter
		)

		verbosity = parser.add_argument_group(title="Verbosity levels", description="Select the verbosity level. Defaults to Warning.")
		verbosity_exclusive = verbosity.add_mutually_exclusive_group()
		verbosity_exclusive.add_argument("-s", "--silent", action="store_true", help="Show critical errors only.")
		verbosity_exclusive.add_argument("-v", "--verbose", action="store_true", help="Show everything.")
		verbosity_exclusive.add_argument("-d", "--debug", action="store_true", help="Show everything and debug logs.")
		
		self.args = parser.parse_args()

		params = self.get_params()

		logger.setLevel(logging.DEBUG)

		file = logging.FileHandler("debug.log")
		console = logging.StreamHandler()

		format = "%(levelname)s - %(asctime)s:\n\t%(message)s"
		formatter = logging.Formatter(format)

		file.setFormatter(formatter)
		console.setFormatter(CustomFormatter(format))

		if params["silent"]:
			file.setLevel(logging.CRITICAL)
			console.setLevel(logging.CRITICAL)
		elif params["verbose"]:
			file.setLevel(logging.INFO)
			console.setLevel(logging.INFO)
		elif params["debug"]:
			file.setLevel(logging.DEBUG)
			console.setLevel(logging.DEBUG)
		else:
			file.setLevel(logging.WARNING)
			console.setLevel(logging.WARNING)
		
		logger.addHandler(file)
		logger.addHandler(console)
	
	def get_params(self):
		return vars(self.args)

class CustomFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

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
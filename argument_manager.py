import argparse, sys, os

class arg_manager():
	args = None

	def __init__(self):
		parser = argparse.ArgumentParser(
			description="Utility tool to backup MySQL databases in AWS with Boto3",
			formatter_class=argparse.ArgumentDefaultsHelpFormatter
		)
		parser.add_argument("-s", "--silent", action="store_true", help="Execute without logs to the terminal")
		
		self.args = parser.parse_args()

		params = self.get_params()

		if params["silent"]:
			sys.stdout = open(os.devnull, 'w')
	
	def get_params(self):
		return vars(self.args)
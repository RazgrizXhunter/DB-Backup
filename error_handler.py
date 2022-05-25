import logging, sys, os, atexit, codecs, socket, glob, time, locale
from mailing import Mailer
from configuration_manager import Configuration_manager

logger = logging.getLogger("logger")

class Error_handler(logging.Handler):
	has_failed = False

	def __init__(self) -> None:
		super().__init__()
		atexit.register(self.wrapup)

	def emit(self, record):
		if (record.levelno >= 40):
			self.has_failed = True
	
	def wrapup(self):
		confmanager = Configuration_manager()
		
		if (not confmanager.config):
			logger.error("Configuration file has not been loaded properly")
			sys.exit()
		
		if (self.has_failed):
			mailer = Mailer(confmanager.config["sendgrid"]["api_key"])
			recipients = confmanager.get_recipients()

			locale.setlocale(locale.LC_TIME, "es_CL")
			date = time.strftime("%a, %d %b %Y %H:%M:%S")

			email = codecs.open("./email/email_body.html", "r")
			contents = email.read()
			email.close()
			
			log_file = open("./backup.log.tmp", "r")
			logs = log_file.read()
			log_file.close()

			contents = contents.replace("{server_name}", socket.gethostname())
			contents = contents.replace("{log}", logs)
			contents = contents.replace("{date}", date)

			mail = {
				"from": confmanager.config["sendgrid"]["sender"],
				"to": recipients,
				"subject": "Backup needs attention",
				"contents": contents
			}

			mailer.compose(mail)
			mailer.send()
			
			self.cleanup()
			print("exiting")
	
	def cleanup(self):
		for file in glob.glob("*.tmp"):
			os.remove(file)

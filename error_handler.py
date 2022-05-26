import logging, sys, os, atexit, codecs, socket, glob, time, locale, inspect
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
		elif(record.levelno == 50):
			logger.warning("Terminating.")
			sys.exit()
	
	def wrapup(self):
		logger.debug("Wrapping up")
		
		if (self.has_failed):
			email_sent = self.send_error_mail()
			
		self.cleanup()
	
	def cleanup(self):
		logger.debug("Removing temporary files")
		for file in glob.glob("*.tmp"):
			os.remove(file)
	
	def send_error_mail(self) -> bool:
		logger.debug("Sending notification email")
		confmanager = Configuration_manager()
		
		if (not confmanager.config):
			logger.critical("Configuration file has not been loaded properly")
		
		mailer = Mailer(confmanager.config["sendgrid"]["api_key"])
		recipients = confmanager.get_recipients()

		date = ""

		try:
			locale.setlocale(locale.LC_TIME, "es_CL.utf8")
			date = time.strftime("%a, %d %b %Y %H:%M:%S")
		except Exception as e:
			logger.error(f"Time locale could not be set, email will be sent without date.\n\t{e}")
		
		try:
			email = codecs.open("./email/email_body.html", "r")
			contents = email.read()
			email.close()
		except Exception as e:
			logger.error(f"Could not load email template")
			return False
		
		try:
			log_file = open("./backup.log.tmp", "r")
			logs = log_file.read()
			log_file.close()
		except Exception as e:
			logger.error(f"Could not load temporary log")
			return False

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

		# try:
		# 	logger.debug(f"Mail was to be sent with:\n\t{logs}") # We don't wanna fill everyone's inbox with junk
		# 	mailer.send()
		# except Exception as e:
		# 	logger.error(f"Could not send mail")
		# 	return False

		return True

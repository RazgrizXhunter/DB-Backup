import logging, sys, os, atexit, codecs, socket, glob, time, locale
from modules.mailing import Mailer
from modules.configuration_manager import Configuration_manager
from modules.custom_alerts import Custom_alerts
from modules.file_manager import File_manager
from modules.innova_monitor import Innova_monitor

logger = logging.getLogger("logger")

class Error_handler(logging.Handler):
	has_failed = False

	def __init__(self) -> None:
		super().__init__()
		atexit.register(self.wrapup)

		self.confmanager = Configuration_manager()

	def emit(self, record):
		if (record.levelno >= 40):
			self.has_failed = True
		
		if(record.levelno == 50):
			logger.warning("Terminating.")
			sys.exit()
	
	def wrapup(self):
		innova_monitor = Innova_monitor()

		logger.debug("Wrapping up")
		self.alert_manager = Custom_alerts()

		if (self.alert_manager.space_alert()):
			self.has_failed = True
		
		if (self.has_failed):
			email_sent = self.send_error_mail()
			
		self.cleanup()
		
		if (innova_monitor.ping()):
			innova_monitor.checkout()
		else:
			logger.warning("Innova Monitor unresponsive")
	
	def cleanup(self):
		logger.debug("Removing temporary files")
		for file in glob.glob("*.tmp"):
			os.remove(file)
	
	def send_error_mail(self) -> bool:
		logger.debug("Sending notification email")
		file_manager = File_manager()
		
		if (not self.confmanager.config):
			logger.critical("Configuration file has not been loaded properly")
		
		mailer = Mailer(self.confmanager.config["sendgrid"]["api_key"])
		recipients = self.confmanager.get_recipients()

		date = ""

		try:
			locale.setlocale(locale.LC_TIME, "es_CL.utf8")
			date = time.strftime("%a, %d %b %Y %H:%M:%S")
		except Exception as e:
			logger.warning(f"Time locale could not be set, email will be sent without date.\n\t{e}")
		
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

		contents = contents.replace("{server_name}", file_manager.get_hostname())
		contents = contents.replace("{log}", logs)
		contents = contents.replace("{date}", date)

		mail = {
			"from": self.confmanager.config["sendgrid"]["sender"],
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

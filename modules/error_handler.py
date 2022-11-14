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
		self.innova_monitor = Innova_monitor()
		self.alert_manager = Custom_alerts()

	def emit(self, record):
		if (record.levelno >= 40):
			self.has_failed = True
		
		if(record.levelno == 50):
			logger.warning("Terminating.")
			sys.exit()
	
	def wrapup(self):
		logger.debug("Wrapping up")

		if (self.innova_monitor.ping()):
			self.innova_monitor.checkout()
		else:
			logger.warning("Innova Monitor unresponsive")

		if (self.alert_manager.space_alert()):
			logger.error("The instance is running out of space")
		
		if (self.has_failed):
			self.send_error_mail()
			
		self.cleanup()
		
	
	def cleanup(self):
		logger.debug("Removing temporary files")
		for file in glob.glob("*.tmp"):
			os.remove(file)
	
	def send_error_mail(self) -> bool:
		logger.debug("Sending notification email")
		
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

		contents = contents.replace("{server_name}", File_manager.get_hostname())
		contents = contents.replace("{ip}", self.confmanager.config["instance"]["ip"] if "ip" in self.confmanager.config["instance"] else self.innova_monitor.my_ip())
		contents = contents.replace("{log}", logs)
		contents = contents.replace("{date}", date)

		mail = {
			"from": self.confmanager.config["sendgrid"]["sender"],
			"to": recipients,
			"subject": "Backup needs attention",
			"contents": contents
		}

		mailer.compose(mail)

		try:
			mailer.send()
			logger.warning("E-Mail sent")
		except Exception as e:
			logger.error(f"Could not send mail.\n\t{e}")
			return False

		return True

import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger("logger")

class Mailer:
	api_key = None
	client = None

	def __init__(self, api_key: str):
		self.client = SendGridAPIClient(api_key)
	
	def compose(self, mail: dict):
		self.mail = Mail(
			from_email=mail["from"],
			to_emails=mail["to"],
			subject=mail["subject"],
			html_content=mail["contents"]
		)
	
	def send(self):
		if (not self.mail or not self.client): return False

		try:
			response = self.client.send(self.mail)
		except Exception as e:
			logger.error(f"Could not send email.\n{e}")
			return False
		
		return response.status_code

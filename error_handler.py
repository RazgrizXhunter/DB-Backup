import logging, sys

class Error_handler(logging.Handler):
	def emit(self, record):
		if (record.levelno >= 40):
			# Send e-mail
			print("email sent")
			sys.exit()

# mailer = Mailer(confmanager.config["sendgrid"]["api_key"])
# recipients = toListOfTuples(confmanager.config["responsibles"])

# mail = {
# 	"from": "algontama@gmail.com",
# 	"to": recipients,
# 	"subject": "Sending with Twilio SendGrid is Fun",
# 	"contents": "<strong>and easy to do anywhere, even with Python</strong>"
# }
# mailer.compose(mail)

# mailer.send()
def send_email(mailing_list):
	try:

		import smtplib
		from email.mime.multipart import MIMEMultipart
		from email.mime.text import MIMEText
		from details import GMAIL_EMAILID, GMAIL_PASSWORD
		

		email_id = GMAIL_EMAILID
		password = GMAIL_PASSWORD

		from_addr = email_id

		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(email_id,password)
		
		for entry in mailing_list:
			item_list = mailing_list[entry]

			to_addr = entry
			msg = []
			for item in item_list:
				_ = "<a href='www.amazon.in/dp/" + str(item.item_asin) + "' _blank='true'>" + item.name + ' has a new price of ' + str(item.cur_price) + "</a>"
				msg.append(_)
			
			body = '<br>'.join(msg)

			msg = MIMEMultipart()
			msg['From'] = from_addr
			msg['To'] = to_addr
			msg['Subject'] = "Price Alert!!"
			msg.attach(MIMEText(body, 'html'))
			msg = msg.as_string()
			server.sendmail(from_addr, to_addr, msg)

		server.quit()
		# print('Done!')
	except:
		pass


def send_single_mail(email, subject, body):
	try:
		import smtplib
		from email.mime.multipart import MIMEMultipart
		from email.mime.text import MIMEText
		from details import GMAIL_EMAILID, GMAIL_PASSWORD

		email_id = GMAIL_EMAILID
		password = GMAIL_PASSWORD

		from_addr = email_id

		server = smtplib.SMTP('smtp.gmail.com',587)
		server.starttls()
		server.login(email_id, password)

		msg = MIMEMultipart()
		msg['From'] = from_addr
		msg['To'] = email
		msg['Subject'] = subject
		msg.attach(MIMEText(body, 'html'))
		msg = msg.as_string()
		server.sendmail(from_addr, email, msg)
		server.quit()
		print('Mail sent!, check email')
	except:
		print('Error occurred, email not sent')
		pass
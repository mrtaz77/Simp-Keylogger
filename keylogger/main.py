import os

from pynput.keyboard import Key, Listener

buffer = ""
keystroke_count = 0
line_count = 0

def on_press(key):
	# print("{0} pressed".format(key),end=" ")
	global buffer, keystroke_count, line_count
	if hasattr(key, 'char'):
		buffer += str(key.char)
	elif key == Key.enter:
		buffer += "\n"
		line_count += 1
	elif key == Key.space:
		buffer += " "
	keystroke_count += 1

def info():
    return """\n\
Text length : {0}\n\
No of keystrokes : {1}\n\
No of lines : {2}""".format(len(buffer), keystroke_count,line_count + 1)

def write_log():
	script_directory = os.path.dirname(os.path.abspath(__file__))
	log_file_path = os.path.join(script_directory, "log.txt")
	with open(log_file_path,"w") as out:
		out.write(buffer)
		out.write(info())

def on_release(key):
	# break loop on pressing esc
	if key == Key.esc :
		write_log()
		return False

# what to do when a key is pressed and released respectively
with Listener(on_press = on_press, on_release = on_release) as listener:
	listener.join()
from cryptography.fernet import Fernet

import os

script_directory = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(script_directory, "enc.txt")

enc_log = os.path.join(script_directory,"enc-log.txt")
enc_system = os.path.join(script_directory,"enc-system.txt")
enc_clipboard = os.path.join(script_directory,"enc-clipboard.txt")

log_file_path = os.path.join(script_directory, "log.txt")
system_info_path = os.path.join(script_directory, "system_info.txt")
clipboard_path = os.path.join(script_directory, "clipboard.txt")

try:
	with open(key_path, "r") as k:
		key = k.read()
except:
	print("Key not found")
	exit(1)


fernet = Fernet(key)

def decrypt_file():
	files_to_decrypt = [log_file_path, clipboard_path, system_info_path]
	encrypted_files = [enc_log, enc_clipboard, enc_system]
	enc_idx = 0
	for file in files_to_decrypt:
		try:
			with open(encrypted_files[enc_idx], 'rb') as f:
				data = f.read()
		except:
			print("File not found: ", encrypted_files[enc_idx])
			continue
		
		try:
			decrypted_text = fernet.decrypt(data)
		except:
			print("Invalid key for decrypting: ", encrypted_files[enc_idx])
			continue

		with open(file, 'wb') as f:
			f.write(decrypted_text)
		
		enc_idx += 1

if __name__ == "__main__":
	decrypt_file()
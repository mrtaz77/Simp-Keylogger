from cryptography.fernet import Fernet
import os

script_directory = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(script_directory,"enc.txt")
key = Fernet.generate_key()
with open(key_path, 'wb') as f:
    f.write(key)
    print("Key generated")
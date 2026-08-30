import os
from dotenv import load_dotenv

print("Current working directory:", os.getcwd())

loaded = load_dotenv()

print(loaded)

device_username = os.getenv("DEVICE_USERNAME")
print(device_username)
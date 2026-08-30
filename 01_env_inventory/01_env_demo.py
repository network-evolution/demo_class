import os
from dotenv import load_dotenv, find_dotenv, dotenv_values

print("Current working directory:", os.getcwd())

loaded = load_dotenv()

print(loaded)

device_username = os.getenv("DEVICE_USERNAME")
device_password = os.getenv("DEVICE_PASSWORD")
device_host = os.getenv("DEVICE_HOST")
missing_value = os.getenv("UNKNOWN_KEY", "ABCD")

dotenv_path = find_dotenv()
print(f".ENV Path:  {dotenv_path}")

dict_values = dotenv_values()

print(dir(dict_values))
print(type(dict_values))
print(dict_values)

# for key in dict_values:
#     print(key)
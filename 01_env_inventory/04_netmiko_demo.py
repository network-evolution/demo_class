import os

import yaml
from dotenv import load_dotenv
from netmiko import ConnectHandler

load_dotenv()

with open("inventory.yaml", "r") as f:
    inventory = yaml.safe_load(f.read())

sw01 = inventory["devices"]["sw01"]
for key, value in sw01.items():
    if isinstance(value, str):
        sw01[key] = os.path.expandvars(value)
        
print(sw01)

connection = ConnectHandler(
    device_type=sw01["device_type"],
    host=sw01["host"],
    username=sw01["username"],
    password=sw01["password"],
    port=sw01["port"],
)

print(connection.send_command("show version"))
print(connection.send_command("show clock"))

connection.disconnect()
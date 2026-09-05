import os,sys
import paramiko
import yaml
from pprint import pprint

from dotenv import load_dotenv

load_dotenv()

INVENTORY_FILE = "inventory.yaml"

with open(INVENTORY_FILE, "r") as f:
   yaml_raw = f.read()
    
inventory = yaml.safe_load(yaml_raw)

for device_name, details in inventory['devices'].items():
    for key, value in details.items():
        # print(key)
        # print(value)
        if isinstance(value, str):
            details[key] = os.path.expandvars(value)

# pprint(inventory)

sw01 = inventory['devices']['sw01']

# print(sw01)

def connect(device):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # print(f"Function executed on {device}")
    
    # print("Connecting to the device")
    client.connect(
        hostname=device['host'],
        port=device['port'],
        username=device['username'],
        password=device['password'],
        look_for_keys=False,
        allow_agent=False,
        timeout=10
    )
    return client


def run_exec_command(client, command):
    stdin, stdout, stderr = client.exec_command(command,timeout=10)
    output = stdout.read().decode()
    error = stderr.read().decode()
    return output, error

# sw01 = connect(sw01)
# output = run_exec_command(sw01, "show version")
# print(output)

#################



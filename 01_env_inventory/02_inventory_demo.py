import yaml
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

INVENTORY_FILE = "inventory.yaml"

with open(INVENTORY_FILE, "r") as f:
   yaml_raw = f.read()
    
inventory = yaml.safe_load(yaml_raw)
# pprint(inventory)

for device_name, details in inventory['devices'].items():
    # print(device_name)
    # print(details)
    for key, value in details.items():
        # print(key)
        # print(value)
        if isinstance(value, str):
            details[key] = os.path.expandvars(value)

pprint(inventory)
        

import pyeapi

import os
import yaml
from dotenv import load_dotenv
from pprint import pprint
load_dotenv()

with open("inventory.yaml", "r") as f:
    inventory = yaml.safe_load(f.read())

sw01 = inventory["devices"]["sw01"]
for key, value in sw01.items():
    if isinstance(value, str):
        sw01[key] = os.path.expandvars(value)

# print(sw01)


node = pyeapi.connect(
    transport='https',
    host=sw01['host'],
    port=sw01['eapi_port'],
    username=sw01['username'],
    password=sw01['password'],
    return_node=True
)

results = node.enable(["show version", "show clock"])
# pprint(results[1])

show_version_result = results[0]['result']
show_clock_result = results[1]['result']

# print(show_version_result)

print(f"Model     :{show_version_result['modelName']}")
print(f"Versio    :{show_version_result['version']}")
print(f"SN        :{show_version_result['serialNumber']}")

print(show_clock_result)
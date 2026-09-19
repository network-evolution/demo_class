import requests
import os, yaml
import urllib3

from dotenv import load_dotenv
from pprint import pprint

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open("inventory.yaml", "r") as f:
    inventory = yaml.safe_load(f.read())

sw01 = inventory["devices"]["sw01"]
for key, value in sw01.items():
    if isinstance(value, str):
        sw01[key] = os.path.expandvars(value)

# print(sw01)

payload = {
    "jsonrpc": "2.0",
    "method": "runCmds",
    "params": {
        "version": 1,
        "cmds": ["show version", "show clock"],
        "format": "json",
    },
    "id": "class082026-demo",
}

url = f"https://{sw01['host']}:{sw01['eapi_port']}/command-api"

# print(url)

response = requests.post(url=url,
                         json=payload,
                         auth=(sw01['username'],sw01['password']),
                         verify=False,
                         timeout=10
                         )

# body = response.json()

# pprint(body)

response.raise_for_status()

body = response.json()

if "error" in body:
    raise RuntimeError(f"eAPI returned an Error: {body['error']}")

show_version_result, show_clock_result = body["result"]

# print(show_clock_result)

print(f"Model     :{show_version_result['modelName']}")
print(f"Versio    :{show_version_result['version']}")
print(f"SN        :{show_version_result['serialNumber']}")

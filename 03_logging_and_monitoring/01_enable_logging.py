import os
import sys

import pyeapi
import yaml
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()
with open("inventory.yaml") as f:
    devices = yaml.safe_load(f)["devices"]
    print(devices)
for device in devices.values():
    for key, value in device.items():
        if isinstance(value, str):
            device[key] = os.path.expandvars(value)      
            
# print(devices)
# 01 import logging
import logging
from logging.handlers import RotatingFileHandler

# Folder for log file
LOG_DIR = os.path.join(os.path.dirname(__file__),"logs")
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(device_name):
    # 02 Define Logger
    logger = logging.getLogger(device_name)
    
    # 03 Set level
    logger.setLevel(logging.DEBUG)

    # 04 Create Handler
    file_handler_info = RotatingFileHandler(os.path.join(LOG_DIR, f"{device_name}_info.log" ), mode="a", maxBytes=500 * 1024, backupCount=5)
    file_handler_debug = RotatingFileHandler(os.path.join(LOG_DIR, f"{device_name}_debug.log" ), mode="a", maxBytes=500 * 1024, backupCount=5)
    stream_handler = logging.StreamHandler(sys.stdout)

    #05 Set level for each handlers
    file_handler_info.setLevel(logging.INFO)
    file_handler_debug.setLevel(logging.DEBUG)
    stream_handler.setLevel(logging.WARNING)
    
    #06 Formatter
    formatter = logging.Formatter('%(asctime)s - %(process)d-  %(name)s - %(levelname)s - %(message)s')
    file_handler_info.setFormatter(formatter)
    file_handler_debug.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    
    #07 Add Handler to logger
    logger.addHandler(file_handler_info)
    logger.addHandler(file_handler_debug)
    logger.addHandler(stream_handler)
    
    return logger

def arista_monitor(device_name, device):
    print(device_name)
    logger = get_logger(device_name)
    logger.info("###### Validation started ########")

    try:
        print(f"\n{'#' * 55}\nConnecting to the Device {device_name}\n{'#' * 55}")
        logger.info(f"Connecting to the Device {device_name}")
        node = pyeapi.connect(transport="https",
                              host=device["host"],
                              port=device["eapi_port"],
                              username=device["username"],
                              password=device["password"],
                              return_node=True)
        
        logger.info("Executing 'show interfaces status' and 'show ip ospf neighbor'")        
        output = node.enable(["show interfaces status", "show ip ospf neighbor"])
        # pprint(output)
        interfaces = output[0]["result"]["interfaceStatuses"]
        ospf = output[1]["result"]
        # pprint(interfaces)
        # pprint(ospf)
        
        logger.info("Received Output")
        logger.debug(f"Interface Output is:\n {interfaces}")
        logger.debug(f"OSPF Output is:\n {ospf}")        

        for intf, details in interfaces.items():
            status = details["linkStatus"]
            if status == "connected":
                logger.info(f"Interface {intf} is UP")
            else:
                logger.critical(f"Interface {intf} is DOWN ({status})")

        neighbors = ospf["vrfs"]["default"]["instList"]["1"]["ospfNeighborEntries"] if ospf["vrfs"] else []
        if not neighbors:
            logger.critical("No OSPF neighbors found")
            
        print(neighbors)

    except pyeapi.eapilib.ConnectionError:
        print("Connection Error")
        logger.critical("Unable to connect")
    except Exception as e:
        logger.error(f"Something went wrong: {e}")
        

for name, device in devices.items():
    # print(name, device)
    arista_monitor(name, device)
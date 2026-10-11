import os
import time
import yaml
from dotenv import load_dotenv
from netmiko import ConnectHandler

load_dotenv()

results = {}
with open("inventory.yaml", "r") as f:
    inventory = yaml.safe_load(f.read())

devices = inventory["devices"]
for name, device in devices.items():
    for key, value in device.items():
        if isinstance(value, str):
            device[key] = os.path.expandvars(value)

# print(devices)

def connect_and_run(name, device, command="show ip int brief"):
    print(f"Connecting to the device {name}")
    start = time.perf_counter()
    # print(start - time.perf_counter())
    try:
        connection = ConnectHandler(
            device_type=device["device_type"],
            host=device["host"],
            port=device["port"],
            username=device["username"],
            password=device["password"],
        )
        output = connection.send_command(command)
        print(output)
        connection.disconnect()
        status = "OK"
        
    except Exception as exc:
        output = str(exc)
        print(output)
        status = "FAILED"
           
    duration = time.perf_counter() - start
    results[name] = {"status": status, "duration": duration, "output": output}


def print_report(label, total_duration):
    print(f"\n--- {label} ---")
    for name in devices:
        r = results[name]
        print(f"  {name:10s} status={r['status']:7s} time={r['duration']:.2f}s")
    print(f"  TOTAL elapsed: {total_duration:.2f}s")   

############ WITHOUT threading sequential
# results.clear()
# start_sequential = time.perf_counter()

# for name, device in devices.items():
#     # print(name)
#     # print(device)
#     connect_and_run(name, device)
    
# sequential_duration = time.perf_counter() - start_sequential
# print_report("WITHOUT threading sequential", sequential_duration)

########### With Threading

import threading
results.clear()

start_thread = time.perf_counter()

threads = []

for name, device in devices.items():
    t = threading.Thread(target=connect_and_run, args=(name, device), name=name)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
  
threaded_duration = time.perf_counter() - start_thread
print_report("WITH threading (concurrent)", threaded_duration)



    
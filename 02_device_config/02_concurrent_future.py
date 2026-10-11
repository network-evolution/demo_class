import os
import time

import yaml
from dotenv import load_dotenv
from netmiko import ConnectHandler

load_dotenv()

with open("inventory.yaml", "r") as f:
    inventory = yaml.safe_load(f.read())

devices = inventory["devices"]
for name, device in devices.items():
    for key, value in device.items():
        if isinstance(value, str):
            device[key] = os.path.expandvars(value)



def connect_and_run(name, device, command="show ip int brief"):
    start = time.perf_counter()
    print(start)
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
        status = "FAILED"

    duration = time.perf_counter() - start
    return {"name": name, "status": status, "duration": duration, "output": output}


# start_sequential = time.perf_counter()

# for name, device in devices.items():
#     connect_and_run(name, device)

# sequential_duration = time.perf_counter() - start_sequential
# print(f"--- WITHOUT concurrency (sequential) --- total={sequential_duration:.2f}s")

############# With Concurrent Futures ###########

from concurrent.futures import ThreadPoolExecutor, as_completed

# start_map = time.perf_counter()
# print(devices.keys())
# with ThreadPoolExecutor(max_workers=len(devices)) as executor:
#     map_results = list(executor.map(connect_and_run, devices.keys(), devices.values()))
    
# map_duration = time.perf_counter() - start_map

# for r in map_results:
#     print(f" {r['name']}    status={r['status']}     time={r['duration']:.2f}s")
# print(f" TOTAL time: {map_duration:.2f}")

############### Concurrent Futures submit + as_completed

start_submit = time.perf_counter()

with ThreadPoolExecutor(max_workers=len(devices)) as executor:
    future_to_name = {executor.submit(connect_and_run, name, device): name
                     for name, device in devices.items()}
    
    
    for future in as_completed(future_to_name):
        name = future_to_name[future]
        r = future.result()
        print(f"  [{time.perf_counter() - start_submit:.2f}s] {r['name']:10s} "
              f"status={r['status']:7s} time={r['duration']:.2f}s")  
        
submit_duration = time.perf_counter() - start_submit
print(f"  TOTAL elapsed: {submit_duration:.2f}s  (printed in FINISH order)")
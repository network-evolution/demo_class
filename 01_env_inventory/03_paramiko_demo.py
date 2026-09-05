import os,sys, time
import paramiko
import yaml
from pprint import pprint

from dotenv import load_dotenv

def load_inventory():
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
    
    return inventory["devices"]

# pprint(inventory)

# sw01 = inventory['devices']['sw01']

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

################# invoke shell #####################

def read_channel(shell, wait_time=1.5):
    time.sleep(wait_time)
    output = ""
    while shell.recv_ready():
        output += shell.recv(65535).decode(errors="ignore")
        time.sleep(0.1)
    return output

def run_interactive_shell(client, commands):
    shell = client.invoke_shell()
    banner = read_channel(shell, wait_time=1.5)
    shell.send("terminal length 0\n")
    read_channel(shell)
    
    results = {}
    for command in commands:
        shell.send(command + "\n")
        results[command] = read_channel(shell)

    shell.close()
    return banner, results

def main():
    devices = load_inventory()
    print(devices)

    # print("=" * 70)
    # print("DEMO A: paramiko exec_command()  (one-shot, Linux-style)")
    # print("=" * 70)
    
    # device = devices["sw01"]
    # print(device)
    
    # try:
    #     client = connect(device)
    #     output, errors = run_exec_command(client, "show version")
    #     print(output)
        
    # except paramiko.AuthenticationException:
    #     print("Authentication failed")
    # finally:
    #     client.close()
    
    ######## invoke shell example ##########
    print("\n" + "=" * 70)
    print("INVOKE SHELL")
    print("\n" + "=" * 70)
    
    show_commands = ["show version", "show clock"]
    
    for name, device in devices.items():
        print(f"\n--- Connecting to {name} ({device['host']}:{device['port']}) ---")
        print(device)
    
        try:
            client = connect(device)
            banner, results = run_interactive_shell(client, show_commands)
            print(f"[{name}] login banner/prompt:\n{banner}")
            
            # print(results)
            for command, output in results.items():
                print(f"[{name}] output of '{command}':\n{output}")
            
        
        except paramiko.AuthenticationException:
            print("Authentication Failed")
        except (paramiko.SSHException, OSError) as exc:
            print(f"[{name}] Could not connect: {exc}")
        finally:
            client.close()
            
main()
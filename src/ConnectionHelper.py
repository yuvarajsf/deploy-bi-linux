import paramiko
import time
import os
import json

class SSHConnectionManager:
    def __init__(self, host, username, password, port=22):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.is_connected = False

    def connect(self):
        try:
            os.system('cls')
            self.ssh_client.connect(self.host, port=self.port, username=self.username, password=self.password)
            self.is_connected = True
            print("-"*40)
            print("[+] SSH connection established.")
            config = {
                'username': self.username,
                'password': self.password,
                'server': self.host
            }

            current_user = os.getlogin()
            config_file_path = fr"C:\Users\{current_user}\.wslconfig.json"
            with open(config_file_path, "w") as f:
                json.dump(config, f)
            print("[+] Your SSH session saved successfully!")
            print("-"*40)

        except paramiko.AuthenticationException:
            print("[-] Authentication failed. Please check your credentials.")
        except paramiko.SSHException as e:
            print(f"[-] Unable to establish SSH connection: {e}")
        except Exception as e:
            print(f"[-] Exception occurred: {e}")

    def execute_command(self, command, needSudo=True, showOutput=True):
        if not self.is_connected:
            print("SSH connection is not established. Connecting now...")
            self.connect()

        try:
            if not needSudo:
                sudo_command = command
            else:
                sudo_command = f"echo '{self.password}' | sudo -S {command}"

            stdin, stdout, stderr = self.ssh_client.exec_command(sudo_command)
            if (type):
                output = stdout.read().decode("utf-8")
                output += stderr.read().decode("utf-8")
                print(f"\n{output}")
        except Exception as e:
            print(f"Error executing command: {e}")

    def close_connection(self):
        if self.is_connected:
            self.ssh_client.close()
            self.is_connected = False
            print("SSH connection closed.")

import os
import json

from src.ConnectionHelper import SSHConnectionManager
    

prerequired_items = [
    'update',
    'nginx',
    'zip',
    'libgdiplus',
    'pv',
    'python3-pip'
]

#helper methods
def check_exisiting_session():
    try:
        current_user = os.getlogin()
        config_file_path = fr"C:\Users\{current_user}\.wslconfig.json"
        if (os.path.exists(config_file_path)):
           with open(config_file_path, 'r') as file:
                config = json.load(file)
                username = config.get('username')
                password = config.get('password')
                server = config.get('server')
                if username and password and server:
                    return [True,username, password, server]
        else:
            return [False]
    except Exception as e:
        return [False]

if __name__ == "__main__":
    ssh = None
    try:
        while True:
            print("-"*40)
            print("1. Connect to SSH")
            print("2. Install prerequisites")
            print("3. Install and Deploy Build")
            print("4. Update Build")
            print("5. Patch work")
            print("6. Clear & Show Option")
            print("7. Exit and close connection")
            print("-"*40)
            choice = int(input("==> "))
            os.system('cls')

            if choice == 1:
                [status, uname, passwd, host] = check_exisiting_session()
                if (status):
                    resp = input("[+] Existing session found. Do you want to use it? (y/n)")
                    if resp.lower() == 'y':
                        ssh = SSHConnectionManager(host, uname, passwd)
                        ssh.connect()
                        continue
                server = input("IP :==> ")
                username = input("Username :==> ")
                password = input("Password :==> ")
                ssh = SSHConnectionManager(server, username, password)
                ssh.connect()

            elif choice == 2:
                if not ssh:
                    print("[-] SSH connection is not established. Please connect first.")
                    continue
                # Initally update the system
                command = "sudo apt-get update"
                ssh.execute_command(command)
                for item in prerequired_items:
                    print("[+] Installing", item)
                    command = f"sudo apt-get install -y {item}"
                    ssh.execute_command(command)
                print("[+] Prerequisites installed successfully.")

            elif choice == 3:
                if not ssh:
                    print("[-] SSH connection is not established. Please connect first.")
                    continue

                build_url = input("Build URL :==> ")

                resp = input("[+] Do you want to extract in custom folder (default no)? (y/n)")
                folder = None
                if resp.lower() == 'y':
                    folder = input("Custom Foldername :==> ")
                    command = f"mkdir {folder}"
                    ssh.execute_command(command)

                # download the build source from internet
                print("[+] Downloading the build....")
                file_name = build_url.split("/")[-1]
                if folder:
                    command = f"wget {build_url} -O ./{folder}/build.zip"
                else:
                    command = f"wget {build_url} -O build.zip"

                ssh.execute_command(command)
                print("[+] Build downloaded successfully.")

                # Extract the downloaded build
                print("[+] Extracting the build....")
                if folder:
                    command = f"unzip ./{folder}/build.zip -d ./{folder}"
                else:
                    command = f"unzip build.zip"

                ssh.execute_command(command)
                print("[+] Build extracted successfully.")
                


                # Deploy the build
                print("[+] Deploying the build....")
                extracted_folder = "BoldBIEnterpriseEdition-Linux"
                if folder:
                    command = f"cd ./{folder}/{extracted_folder}/ && echo {ssh.password} | sudo -S bash install-boldbi.sh -i new -u root -h http://{ssh.host} -n true"
                else:
                    command = f"cd ./{extracted_folder}/ && echo {ssh.password} | sudo -S bash install-boldbi.sh -i new -u root -h http://{ssh.host} -n true"

                ssh.execute_command(command, False)
                print("[+] Build deployed successfully.")

            elif choice == 4:
                print("update build")
            
            elif choice == 5:
                print("patch work")

            elif choice == 6:
                os.system('cls')
                continue

            elif choice == 7:
                print("Exiting ...")
                if ssh:
                    ssh.close_connection()
                exit(0)

    except KeyboardInterrupt:
        print("\nExiting ...")
        if ssh:
            ssh.close_connection()
        exit(0)
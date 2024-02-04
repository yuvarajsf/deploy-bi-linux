import os
import json
import easygui

from src.ConnectionHelper import SSHConnectionManager

prerequired_items = [
    'nginx',
    'zip',
    'libgdiplus',
    'pv',
    'python3-pip'
]

deployed_location = "/var/www/bold-services/application/bi/dataservice/"

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
            print("6. Revert Patch work")
            print("7. Uninstall Build")
            print("8. Clear & Show Option")
            print("9. Exit and close connection")
            print("-"*40)
            try:
                choice = int(input("==> "))
            except ValueError:
                os.system('cls')
                print("[-] Invalid input. Please enter a valid number.")
                continue

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

                # remove backup folder
                command = "rm -rf ./backup"
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
                print("[!] Please wait, it may take some time to deploy the build....")
                extracted_folder = "BoldBIEnterpriseEdition-Linux"
                if folder:
                    command = f"cd ./{folder}/{extracted_folder}/ && echo {ssh.password} | sudo -S bash install-boldbi.sh -i new -u root -h http://{ssh.host} -n true"
                else:
                    command = f"cd ./{extracted_folder}/ && echo {ssh.password} | sudo -S bash install-boldbi.sh -i new -u root -h http://{ssh.host} -n true"

                ssh.execute_command(command, False)
                ssh.execute_command("export OPENSSL=/etc/ssl/", False)
                print("[+] Build deployed successfully.")

            elif choice == 4:
                print("update build - under development....")
            
            elif choice == 5:
                if not ssh:
                    print("[-] SSH connection is not established. Please connect first.")
                    continue
                try:
                    print("[+] Select patch files to make changes in the build")
                    file_paths = easygui.fileopenbox(title="Select patch file", filetypes=["*.dll"], default="D:/", multiple=True)
                    command = "mkdir backup"
                    ssh.execute_command(command, True, False)
                    
                    if file_paths:
                        for link in file_paths:
                            dll_file_name = link.split("\\")[-1]
                            modified_link = link.replace("\\", "/")
                            print("[+] Uploading: ", dll_file_name)

                            # take backup of the existing file
                            print("[+] Taking backup of existing file....")
                            command = f"cp {deployed_location}{dll_file_name} ~/backup/{dll_file_name}"
                            ssh.execute_command(command)
                            print("[+] Backup taken successfully.")

                            # move the new file to the deployed location
                            print("[+] Moving new patch files to deployed location....")
                            remote_path = f"{deployed_location}"
                            
                            # move files to remote server
                            scp = ssh.ssh_client.open_sftp()
                            scp.put(modified_link, dll_file_name)
                            scp.close()
                            command = f"mv ./{dll_file_name} {remote_path}"
                            ssh.execute_command(command)
                            print("[+] Patch deployed successfully.")
                            

                        # restart BoldBI service
                        print("[+] Restarting BoldBI service....")
                        command = "systemctl restart bold-*"
                        ssh.execute_command(command)
                        print("[+] BoldBI service restarted successfully.")

                    else:
                        print("[-] No file selected.")
                except Exception as e:
                    print("[-] Error occurred: ", e)

            elif choice == 6:
                if not ssh:
                    print("[-] SSH connection is not established. Please connect first.")
                    continue
                try:
                    # Move backup files to deployed location
                    command = f"mv ~/backup/* {deployed_location}"
                    ssh.execute_command(command)
                    print("[+] If backup found, Patch reverted successfully.")
                    
                    # remove backup folder
                    command = "rm -rf ~/backup"
                    ssh.execute_command(command)

                    # restart BoldBI service
                    print("[+] Restarting BoldBI service....")
                    command = "systemctl restart bold-*"
                    ssh.execute_command(command)
                    print("[+] BoldBI service restarted successfully.")
                except Exception as e:
                    print("[-] Error occurred: ", e)

            elif choice == 7:
                if not ssh:
                    print("[-] SSH connection is not established. Please connect first.")
                    continue
                resp = input("[+] Do you want to uninstall the build? (y/n)")
                if resp.lower() == 'y':
                    print("[+] Uninstalling the build....")
                    command = f"cd /var/www/bold-* && echo {ssh.password} | sudo -S bash -c 'echo yes | bash ./uninstall-boldbi.sh'"
                    ssh.execute_command(command, False)
                    print("[+] Build uninstalled successfully.")
                else:
                    print("[-] Uninstall cancelled.")

            elif choice == 8:
                os.system('cls')
                continue

            elif choice == 9:
                print("Exiting ...")
                if ssh:
                    ssh.close_connection()
                exit(0)

    except KeyboardInterrupt:
        print("\nExiting ...")
        if ssh:
            ssh.close_connection()
        exit(0)
import paramiko
from datetime import datetime

def create_remote_folder(server_address, username, password, folder_path):
    # Connect to the remote server
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(server_address, username=username, password=password)

    # Create folder with current date in day-month-year format
    current_date = datetime.now().strftime("%d-%B-%Y")
    command = f"mkdir \"{folder_path}\\{current_date}\""
    stdin, stdout, stderr = ssh_client.exec_command(command)

    # Check if folder creation was successful
    if not stderr.read():
        print(f"Folder created successfully at '{folder_path}' on {server_address}")
    else:
        print(f"Failed to create folder at '{folder_path}' on {server_address}")

    # Close SSH connection
    ssh_client.close()

if __name__ == "__main__":
    # Replace these with your remote server details
    server_address = "192.168.222.150"
    username = 'administrator@lab.local'
    password = ''
    # Specify the desired folder path
    folder_path = r"D:\testing folder"
    # Source an

    create_remote_folder(server_address, username, password, folder_path)

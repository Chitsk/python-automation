import paramiko
import math
from datetime import datetime, timedelta
import logging
import os

# Server and authentication details
server_address = "172.30.32.9"
username = 'administrator@mprlexp.local'
password = ''  # Ensure this is properly escaped or handled securely

# Calculate yesterday's date and format it
yesterday = datetime.now() - timedelta(1)
formatted_date = yesterday.strftime('%d-%b-%Y')

# Paths
new_folder_path = rf'\\172.30.50.149\FileShare BK Attachment4SAP-WMS\{formatted_date}'
existing_folder_path = r'\\172.30.50.149\FileShare BK Attachment4SAP-WMS\WindowsImageBackup'  # Adjust this to your actual path

# Custom log file path
log_file_path = r'C:\Users\Administrator.MPRLEXP\Desktop\script\SAB-BK-Prod\log\04-Attachement-BK-created.log'

# Set up logging
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

def initialize_ssh_connection(server_address, username, password):
    """Initialize SSH connection to the remote server."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_address, port=22, username=username, password=password)
        return ssh
    except paramiko.AuthenticationException:
        error_msg = "Authentication failed. Please check your username and password."
        logging.error(error_msg)
        return None
    except paramiko.SSHException as e:
        error_msg = f"SSH connection failed: {e}"
        logging.error(error_msg)
        return None
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        logging.error(error_msg)
        return None

def folder_exists(ssh, path):
    """Check if a folder exists on the remote server."""
    command = f'powershell -Command "Test-Path -Path \'{path}\'"'
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode().strip()
    return result == 'True'

def get_hostname(ssh):
    """Retrieve the hostname of the remote server using PowerShell."""
    command = 'powershell -Command "hostname"'
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode().strip()

def convert_size(size_bytes):
    """Convert bytes to a more human-readable format."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def create_and_move_folder(ssh, new_folder_path, existing_folder_path):
    """Create a new folder and move the existing folder into it."""
    try:
        # Check if the new folder already exists
        if folder_exists(ssh, new_folder_path):
            logging.info(f"Folder already exists: {new_folder_path}")
        else:
            # Command to create the new folder
            create_folder_command = f'powershell -Command "New-Item -ItemType Directory -Path \'{new_folder_path}\'"'
            stdin, stdout, stderr = ssh.exec_command(create_folder_command)
            error = stderr.read().decode()
            if error:
                logging.error(f"Error creating folder: {error}")
            else:
                logging.info(f"Folder created successfully: {new_folder_path}")

        # Check if the existing folder exists
        if not folder_exists(ssh, existing_folder_path):
            logging.warning(f"Folder to move does not exist: {existing_folder_path}")
        else:
            # Command to move the existing folder to the new folder
            move_folder_command = f'powershell -Command "Move-Item -Path \'{existing_folder_path}\' -Destination \'{new_folder_path}\' -Force"'
            stdin, stdout, stderr = ssh.exec_command(move_folder_command)
            error = stderr.read().decode()
            if error:
                logging.error(f"Error moving folder: {error}")
            else:
                logging.info(f"Folder moved successfully to: {new_folder_path}")

        # ### Command to get the size of the newly created folder
        get_folder_size_command = f'powershell -Command "(Get-ChildItem -Path \'{new_folder_path}\' -Recurse | Measure-Object -Property Length -Sum).Sum"'
        stdin, stdout, stderr = ssh.exec_command(get_folder_size_command)
        folder_size_output = stdout.read().decode().strip()
        folder_size_error = stderr.read().decode()
        if folder_size_error:
            logging.error(f"Error getting folder size: {folder_size_error}")
        else:
            # Extract the folder size
            folder_size = int(folder_size_output)
            # Convert size to a more human-readable format
            formatted_size = convert_size(folder_size)
            logging.info(f"Size of {new_folder_path}: {formatted_size}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

def main():
    ssh = initialize_ssh_connection(server_address, username, password)
    if not ssh:
        return

    try:
        # Get hostname of the remote server and log it
        hostname = get_hostname(ssh)
        logging.info(f"Remote server hostname: {hostname}")
        logging.info(f"Remote server IP: {server_address}")

        create_and_move_folder(ssh, new_folder_path, existing_folder_path)

    finally:
        ssh.close()
        logging.info("SSH connection closed")

# Ensure log directory exists
log_dir = os.path.dirname(log_file_path)
os.makedirs(log_dir, exist_ok=True)

# Run the function
main()

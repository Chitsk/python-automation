import paramiko
import re
import sys

# Define the server and login credentials
server_address = "192.168.222.150"
username = 'administrator@lab.local'
password = ''  # Ensure this is properly escaped or handled securely

# Base path where the folders are located
base_path = r'D:\sharefolder2\backup\data space'

# Log file path
log_file_path = r'C:\Users\csk\Desktop\windowsmgmt\FInal TEST\log\logfile.log'

# Establish SSH connection
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(server_address, 22, username, password)
    print('Connected to the server.')
except Exception as e:
    print(f"An error occurred while connecting to the server: {e}")
    sys.exit(1)

# Redirect stdout and stderr to the log file
sys.stdout = open(log_file_path, 'a')
sys.stderr = sys.stdout

# PowerShell command to list directories with their last write time
list_dirs_command = f'powershell "Get-ChildItem \'{base_path}\' -Directory | Select-Object FullName, LastWriteTime | Sort-Object LastWriteTime"'

def get_oldest_folder():
    try:
        # Execute the command to list directories with their last write time
        stdin, stdout, stderr = ssh.exec_command(list_dirs_command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        if error:
            print(f"Error: {error}")
            return None

        # Print the output for debugging
        print("Command output:\n", output)

        # Split the output into lines and process each line
        lines = output.strip().split('\n')

        # The actual data starts from the third line (headers are the first two lines)
        folder_lines = lines[2:]

        # Extract the folder paths, assuming each line format is: "FullName LastWriteTime"
        folder_paths = []
        for line in folder_lines:
            # Match folder path and ignore date/time part
            match = re.match(r"^(.*\S)(\s+\d+/\d+/\d+\s+\d+:\d+:\d+\s+(AM|PM))$", line.strip())
            if match:
                folder_path = match.group(1).strip()
                folder_paths.append(folder_path)

        if not folder_paths:
            print("No folders found.")
            return None

        # The first folder in the sorted list should be the oldest
        oldest_folder = folder_paths[0]

        print(f"Oldest folder found: {oldest_folder}")

        return oldest_folder

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def delete_remote_folder(folder_path):
    try:
        print(f"Deleting folder: {folder_path}")

        # Command to delete the folder
        delete_command = f'rmdir /S /Q "{folder_path}"'

        # Execute the command to delete the folder
        stdin, stdout, stderr = ssh.exec_command(delete_command)

        # Get the results
        output = stdout.read().decode()
        error = stderr.read().decode()

        # Print results
        if output:
            print(f"Output: {output}")
        if error:
            print(f"Error: {error}")

        print(f"Folder {folder_path} deleted successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    oldest_folder = get_oldest_folder()
    if oldest_folder:
        print(f"Oldest folder to delete: {oldest_folder}")
        delete_remote_folder(oldest_folder)
    else:
        print("No folder to delete.")

# Close SSH connection
ssh.close()

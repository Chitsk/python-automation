import paramiko
import os

def ssh_connect_and_execute(hostname, port, username, password, command, log_file):
    try:
        # Create an SSH client object
        ssh_client = paramiko.SSHClient()
        
        # Automatically add the server's host key (to avoid the need for manual acceptance)
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Establish the SSH connection
        ssh_client.connect(hostname, port, username, password)
        
        # Execute the command on the remote server
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # Retrieve the command output
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        # Filter out unwanted parts from output
        output_lines = output.split('\n')
        output_filtered = '\n'.join(line for line in output_lines if not any(unwanted_part in line for unwanted_part in ["VersionId", "SuccessLogPath", "FailureLogPath", "HResult", "DetailedHResult"]))
        
        # Write filtered output and errors to log file
        with open(log_file, 'a') as f:
            if output_filtered:
                f.write("Output:\n")
                f.write(output_filtered)
            if error:
                f.write("Error:\n")
                f.write(error)
        
        # Close the SSH connection
        ssh_client.close()
        
        return output, error
    
    except paramiko.AuthenticationException:
        return "Authentication failed. Please check your credentials.", None
    except paramiko.SSHException as ssh_exception:
        return f"SSH connection failed: {ssh_exception}", None
    except Exception as e:
        return f"An error occurred: {e}", None

# Server details
server_address = "192.168.222.150"
port = 22
username = 'administrator@lab.local'
password = ''  # Ensure this is properly escaped or handled securely

# Example command to check Windows Backup status using PowerShell
command = 'powershell -Command "Get-WBJob"'

# Path to the log file
log_file= r'C:\Users\csk\Desktop\windowsmgmt\FInal TEST\log\ADL-Backup-Progress-Check.log'

# Connect to the remote server and execute the command
output, error = ssh_connect_and_execute(server_address, port, username, password, command, log_file)

# Check if the output contains "JobState         : Unknown"
if output and "JobState         : Unknown" in output:
    # Run another script file in the same directory
    script_file = r'C:\Users\csk\Desktop\windowsmgmt\FInal TEST\Create-Move-Folder.py'
    if os.path.exists(script_file):
        os.system(f"python \"{script_file}\"")
        
        # Run another script after Create-Move-Folder.py
        another_script_file = r'C:\Users\csk\Desktop\windowsmgmt\FInal TEST\Delete-OldestFolder.py'
        if os.path.exists(another_script_file):
            os.system(f"python \"{another_script_file}\"")
        else:
            with open(log_file, 'a') as f:
                f.write(f"Script file '{another_script_file}' not found.\n")
    else:
        with open(log_file, 'a') as f:
            f.write(f"Script file '{script_file}' not found.\n")
else:
    # Print the output or error to console
    if output:
        print("Output:\n", output)
    if error:
        print("Error:\n", error)

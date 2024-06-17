import paramiko
#calculate disk size of C: and D: in remote windows server over ssh using python script
def convert_bytes(size, unit='GB'):
    """
    Convert bytes to specified unit (default is GB).
    """
    units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
    return size / units[unit]

def get_disk_info(ssh_client, drive, unit='GB'):
    """
    Get disk size and free space for specified drive and convert them to the specified unit.
    """
    stdin, stdout, stderr = ssh_client.exec_command(f"wmic logicaldisk where DeviceID='{drive}' get Size, FreeSpace")
    output = stdout.readlines()
    size_info = [int(x) for x in output[1].split()] if len(output) > 1 else None
    if size_info is not None:
        disk_size = convert_bytes(size_info[0], unit)
        free_space = convert_bytes(size_info[1], unit)
    else:
        disk_size = None
        free_space = None
    return disk_size, free_space

def main():
    port = 22
    hostname = "192.168.222.150"
    username = 'administrator@lab.local'
    password = ''

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(hostname, port, username, password)
        c_drive_size, c_drive_free = get_disk_info(ssh_client, 'C:')
        d_drive_size, d_drive_free = get_disk_info(ssh_client, 'D:')
        print(f"Size of C: drive: {c_drive_size:.2f} GB, Free space: {c_drive_free:.2f} GB")
        print(f"Size of D: drive: {d_drive_size:.2f} GB, Free space: {d_drive_free:.2f} GB")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh_client.close()

if __name__ == "__main__":
    main()

import paramiko

def get_arp_info(hostname, username, password, port=2434):
    try:
        # Create SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the router
        client.connect(hostname, port=port, username=username, password=password)

        # Execute the command to get ARP information
        command = "show arp"
        stdin, stdout, stderr = client.exec_command(command)

        # Read the output
        arp_output = stdout.read().decode('utf-8')

        return arp_output

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        # Close the SSH connection
        client.close()

def main():
    router_hostname = '12.176.237.34'
    ssh_username = 'vlad@uskoinc.com'
    ssh_password = 'Uw2b#1tc4365'
    ssh_port = 2434  # Replace with your actual SSH port

    arp_info = get_arp_info(router_hostname, ssh_username, ssh_password, port=ssh_port)

    print(arp_info)


if __name__ == "__main__":
    main()

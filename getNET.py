import socket
import getmac

def get_remote_mac(hostname):
    try:
        ip_address = socket.gethostbyname(hostname)
        mac_address = getmac.get_mac_address(ip=ip_address)
        return mac_address, ip_address
    except socket.error as e:
        print(f"Error: {e}")
        return None
    except getmac.GetMacError as e:
        print(f"Error: {e}")
        return None

def main():
    hostname = "Usko-1125"
    mac_address, ip = get_remote_mac(hostname)

    if mac_address:
        print(f"{hostname} - {mac_address} - {ip}")
    else:
        print(f"Failed to retrieve MAC address for {hostname}.")

if __name__ == "__main__":
    main()
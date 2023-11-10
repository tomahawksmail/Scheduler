import socket
import getmac
import os
from dotenv import load_dotenv
import pymysql

load_dotenv()

connection = pymysql.connect(host=os.environ.get('DBHOST'),
                             user=os.environ.get('DBUSER'),
                             password=os.environ.get('DBPASSWORD'),
                             database=os.environ.get('DATABASE'))
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
    SQLrequestSelect = """SELECT * from computerlist"""
    try:
        connection.connect()
    except Exception as E:
        print(E)
    else:
        with connection.cursor() as cursor:
            cursor.execute(SQLrequestSelect)
        result = cursor.fetchall()

    for host in result:
        hostname = host[0]
        try:
            mac_address, ip = get_remote_mac(hostname)
        except Exception as E:
            print(E)

        if mac_address:
            print(f"{hostname} - {mac_address} - {ip}")
        else:
            print(f"Failed to retrieve MAC address for {hostname}.")

if __name__ == "__main__":
    main()
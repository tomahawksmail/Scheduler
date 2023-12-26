import paramiko
import os
import time
from dotenv import load_dotenv
import pymysql

load_dotenv()
dir = r"\\shots11\tools\UskoPortalSupplyFiles"
# dir = "\\\\USKO-1125\share"
# dir = r"\\192.168.11.10\devadm\UskoPortalSupplyFiles"

connection = pymysql.connect(host=os.environ.get('DBHOST'),
                             user=os.environ.get('DBUSER'),
                             password=os.environ.get('DBPASSWORD'),
                             database=os.environ.get('DATABASE'))

client = paramiko.client.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def main():
    SQLrequestSelect = """SELECT node from computerlist WHERE `check` = 1"""
    try:
        connection.connect()
    except Exception as E:
        print(E)
    else:
        with connection.cursor() as cursor:
            cursor.execute(SQLrequestSelect)
        result = cursor.fetchall()

        for host in result:
            print(f"Working on a host -  {host[0]}")
            try:
                client.connect(host[0], username=os.environ.get('USER'), password=os.environ.get('PASSWORD'))
                print("---------------------------------------")
                print(f"Connected to {host[0]}")
            except Exception as E:
                print(E)
                SQLrequestSelect = f"INSERT INTO metricsStatus (hostname, task_stamp) VALUES ('{host[0]} - Connection failed', NOW())"""
                with connection.cursor() as cursor:
                    cursor.execute(SQLrequestSelect)
                    connection.commit()
            else:
                try:
                    print(f"Set timezone at {host[0]}")
                    # set timezone
                    client.exec_command(r'tzutil /s "Pacific Standard Time"')

                    print(f"Deleting temporary files from {host[0]}")
                    client.exec_command(
                        r"rd C:\Windows\System32\GroupPolicy\Machine\ /S /Q")
                    client.exec_command(
                        r"rd C:\Windows\System32\GroupPolicy\User\ /S /Q")
                    client.exec_command(
                        r"rd C:\Windows\System32\GroupPolicy\tasks\ /S /Q")

                    # Copy scripts for Shutdown and startup events
                    command = "xcopy " + dir + r"\Machine" + r" C:\Windows\System32\GroupPolicy\Machine /E /H /C /I /Y"
                    client.exec_command(command)
                    command = "xcopy " + dir + r"\User" + r" C:\Windows\System32\GroupPolicy\User /E /H /C /I /Y"
                    client.exec_command(command)
                    command = "xcopy " + dir + r"\tasks" + r" C:\Windows\System32\GroupPolicy\tasks /E /H /C /I /Y "
                    client.exec_command(command)
                    time.sleep(0.1)

                    command = r"""icacls C:\Windows\System32\GroupPolicy\Machine /grant "Users:(OI)(CI)RX" /t"""
                    client.exec_command(command)
                    command = r"""icacls C:\Windows\System32\GroupPolicy\Machine /grant "*S-1-5-11:(OI)(CI)F" /t"""
                    client.exec_command(command)

                    command = r"""icacls C:\Windows\System32\GroupPolicy\User /grant "Users:(OI)(CI)RX" /t"""
                    client.exec_command(command)
                    command = r"""icacls C:\Windows\System32\GroupPolicy\User /grant "*S-1-5-11:(OI)(CI)F" /t"""
                    client.exec_command(command)


                    # Clear all old tasks
                    print(f"Stoping schedule tasks at {host[0]}")
                    print("....................................")
                    client.exec_command(r'schtasks /end /tn  "\UskoInc\local.disconnect"')
                    client.exec_command(r'schtasks /end /tn  "\UskoInc\rdp.disconnect"')
                    client.exec_command(r'schtasks /end /tn  "\UskoInc\lock_"')
                    client.exec_command(r'schtasks /end /tn  "\UskoInc\logon"')
                    client.exec_command(r'schtasks /end /tn  "\UskoInc\unlock_"')
                    #
                    time.sleep(0.1)
                    print(f"Deleting schedule tasks at {host[0]}")
                    print("....................................")
                    client.exec_command(r'schtasks /delete /tn  "\UskoInc\local.disconnect" /F')
                    client.exec_command(r'schtasks /delete /tn  "\UskoInc\rdp.disconnect" /F')
                    client.exec_command(r'schtasks /delete /tn  "\UskoInc\lock_" /F')
                    client.exec_command(r'schtasks /delete /tn  "\UskoInc\logon" /F')
                    client.exec_command(r'schtasks /delete /tn  "\UskoInc\unlock_" /F')
                    time.sleep(0.1)

                    # Applying schedule tasks
                    print(f"Applying schedule tasks at {host[0]}")
                    print("....................................")
                    client.exec_command(
                        r'schtasks /create /xml "C:\Windows\System32\GroupPolicy\tasks\localdisconnect.xml" /tn "\UskoInc\local.disconnect"')
                    client.exec_command(
                        r'schtasks /create /xml "C:\Windows\System32\GroupPolicy\tasks\rdpdisconnect.xml" /tn "\UskoInc\rdp.disconnect"')
                    client.exec_command(
                        r'schtasks /create /xml "C:\Windows\System32\GroupPolicy\tasks\lock.xml" /tn "\UskoInc\lock_"')
                    client.exec_command(
                        r'schtasks /create /xml "C:\Windows\System32\GroupPolicy\tasks\logon.xml" /tn "\UskoInc\logon"')
                    client.exec_command(
                        r'schtasks /create /xml "C:\Windows\System32\GroupPolicy\tasks\unlock.xml" /tn "\UskoInc\unlock_"')
                    time.sleep(0.1)

                    # log task to db
                    SQLrequestSelect = f"INSERT INTO metricsStatus (hostname, task_stamp) VALUES ('{host[0]}', NOW())"""
                    with connection.cursor() as cursor:
                        cursor.execute(SQLrequestSelect)
                        connection.commit()

                    # print(f"Reboot host {host[0]}")
                    # time.sleep(0.5)
                    # client.exec_command(r"shutdown /r /t 00")
                    # time.sleep(3)

                except Exception as E:
                    print(E)
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()

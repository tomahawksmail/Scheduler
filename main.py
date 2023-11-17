import paramiko
import os
import time
from dotenv import load_dotenv
import pymysql


load_dotenv()

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
        print(host[0])
        try:
            client.connect(host[0], username=os.environ.get('USER'), password=os.environ.get('PASSWORD'))
            print(f"Connected to {host[0]}")
        except Exception as E:
            print(E)
        # Copy scripts
        try:
            print(f"Set timezone at {host[0]}")
            # set timezone
            client.exec_command(r'tzutil /s "Pacific Standard Time"')
            # Copy scripts for Shutdown and startup events
            print(f"Copy scripts for Shutdown and startup events at {host[0]}")
            client.exec_command(
                r"xcopy \\shots11\tools\sendmetrics\GroupPolicy\Machine\Scripts\ C:\Scripts\ /E /H /C /I")
            time.sleep(0.1)
            client.exec_command(
                r"xcopy C:\Scripts\ C:\Windows\System32\GroupPolicy\Machine\Scripts\ /E /H /C /I")
            time.sleep(0.1)
            print(f"Deleting files from {host[0]}")
            client.exec_command(
                r"rd C:\Scripts\ /S /Q")
            time.sleep(0.5)


            # Copy scripts for Logoff and Logon events /S /Q /Y /F /H /E /V /-Y /R
            print(f"Copy scripts for Logoff and Logon events at {host[0]}")
            client.exec_command(
                r"xcopy \\shots11\tools\sendmetrics\GroupPolicy\User\Scripts\ C:\Scripts\ /E /H /C /I /Y ")
            time.sleep(0.1)
            client.exec_command(
                r"xcopy C:\Scripts\ C:\Windows\System32\GroupPolicy\User\Scripts\ /E /H /C /I /Y ")
            time.sleep(0.1)
            print(f"Deleting files from {host[0]}")
            client.exec_command(
                r"rd C:\Scripts\ /S /Q")

            # Copy scripts and xml for import schedule tasks
            print(f"Copy scripts and xml for import schedule tasks at {host[0]}")
            client.exec_command(
                r"xcopy \\shots11\tools\sendmetrics\GroupPolicy\Scheduler\ C:\Scheduler\ /E /H /C /I /Y ")
            time.sleep(0.1)
            client.exec_command(
                r"xcopy C:\Scheduler\ C:\Windows\System32\GroupPolicy\Scheduler\ /E /H /C /I /Y ")

            print(f"Stoping schedule tasks at {host[0]}")
            client.exec_command(r'schtasks /end /tn  "\UskoInc\local.disconnect"')
            client.exec_command(r'schtasks /end /tn  "\UskoInc\lockPC"')
            client.exec_command(r'schtasks /end /tn  "\UskoInc\logon"')
            client.exec_command(r'schtasks /end /tn  "\UskoInc\rdp.disconnect"')
            client.exec_command(r'schtasks /end /tn  "\UskoInc\unlockPC"')

            print(f"Deleting schedule tasks at {host[0]}")
            client.exec_command(r'schtasks /delete /tn  "\UskoInc\local.disconnect"')
            client.exec_command(r'schtasks /delete /tn  "\UskoInc\lockPC"')
            client.exec_command(r'schtasks /delete /tn  "\UskoInc\logon"')
            client.exec_command(r'schtasks /delete /tn  "\UskoInc\rdp.disconnect"')
            client.exec_command(r'schtasks /delete /tn  "\UskoInc\unlockPC"')


            print(f"Applying schedule tasks at {host[0]}")
            client.exec_command(r'schtasks /create /xml "C:\Scheduler\local.disconnect.xml" /tn "\UskoInc\local.disconnect"')
            client.exec_command(r'schtasks /create /xml "C:\Scheduler\lock.xml" /tn "\UskoInc\lockPC"')
            client.exec_command(r'schtasks /create /xml "C:\Scheduler\logon.xml" /tn "\UskoInc\logon"')
            client.exec_command(r'schtasks /create /xml "C:\Scheduler\rdp.disconnect.xml" /tn "\UskoInc\rdp.disconnect"')
            client.exec_command(r'schtasks /create /xml "C:\Scheduler\unlock.xml" /tn "\UskoInc\unlockPC"')
            time.sleep(0.5)

            print(f"Deleting files from {host[0]}")
            client.exec_command(
                r"rd C:\Scheduler\ /S /Q")

            print(f"Reboot host {host[0]}")
            time.sleep(0.5)
            client.exec_command(r"shutdown /r /t 00")


        except Exception as E:
            print(E)


        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()



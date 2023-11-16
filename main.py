import paramiko
import re
import os
import time
from dotenv import load_dotenv
import pymysql
import const

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
        client.connect(host[0], username=os.environ.get('USER'), password=os.environ.get('PASSWORD'))
        # Copy scripts
        try:
            # set timezone
            client.exec_command(r'tzutil /s "Pacific Standard Time"')
            # Copy scripts for Shutdown and startup events
            client.exec_command(
                r"xcopy \\shots11\tools\sendmetrics\GroupPolicy\Machine\Scripts\ C:\Scripts\ /E /H /C /I")
            time.sleep(0.1)
            client.exec_command(
                r"xcopy C:\Scripts\ C:\Windows\System32\GroupPolicy\Machine\Scripts\ /E /H /C /I")
            time.sleep(0.1)
            client.exec_command(
                r"rd C:\Scripts\ /S /Q")
            time.sleep(0.5)


            # Copy scripts for Logoff and Logon events /S /Q /Y /F /H /E /V /-Y /R
            client.exec_command(
                r"xcopy \\shots11\tools\sendmetrics\GroupPolicy\User\Scripts\ C:\Scripts\ /E /H /C /I /Y ")
            time.sleep(0.1)
            client.exec_command(
                r"xcopy C:\Scripts\ C:\Windows\System32\GroupPolicy\User\Scripts\ /E /H /C /I /Y ")
            time.sleep(0.1)
            client.exec_command(
                r"rd C:\Scripts\ /S /Q")

            # Copy scripts and xml for import schedule tasks
            client.exec_command(
                r"xcopy \\shots11\tools\sendmetrics\GroupPolicy\Scheduler\ C:\Scheduler\ /E /H /C /I /Y ")
            time.sleep(0.1)
            client.exec_command(
                r"xcopy C:\Scheduler\ C:\Windows\System32\GroupPolicy\Scheduler\ /E /H /C /I /Y ")
            client.exec_command(
                r"rd C:\Scheduler\ /S /Q")

            client.exec_command('schtasks /create /xml "C:\Windows\System32\GroupPolicy\Scheduler\local.disconnect.xml" /tn "\\UskoInc\\local.disconnect"')
            client.exec_command('schtasks /create /xml "C:\Windows\System32\GroupPolicy\Scheduler\lock.xml" /tn "\\UskoInc\\lock"')
            client.exec_command('schtasks /create /xml "C:\Windows\System32\GroupPolicy\Scheduler\logon.xml" /tn "\\UskoInc\\logon"')
            client.exec_command('schtasks /create /xml "C:\Windows\System32\GroupPolicy\Scheduler\\rdp.disconnect.xml" /tn "\\UskoInc\\rdp.disconnect"')
            client.exec_command('schtasks /create /xml "C:\Windows\System32\GroupPolicy\Scheduler\\unlock.xml" /tn "\\UskoInc\\unlock"')


            time.sleep(0.5)
            client.exec_command(r"shutdown /r /t 00")


        except Exception as E:
            print(E)


        cursor.close()
        connection.close()




# delete schedule tasks
# schtasks /end /tn "\UskoInc\1"
# schtasks /delete /tn "\UskoInc\1" /f


if __name__ == "__main__":
    main()



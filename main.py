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


            # #Copy scripts for Logoff and Logon events /S /Q /Y /F /H /E /V /-Y /R
            client.exec_command(
                r"xcopy \\shots11\tools\sendmetrics\GroupPolicy\User\Scripts\ C:\Scripts\ /E /H /C /I /Y ")
            time.sleep(0.1)
            client.exec_command(
                r"xcopy C:\Scripts\ C:\Windows\System32\GroupPolicy\User\Scripts\ /E /H /C /I /Y ")
            time.sleep(0.1)
            client.exec_command(
                r"rd C:\Scripts\ /S /Q")
            time.sleep(0.5)
            client.exec_command(r"shutdown /r /t 00")

            # client.exec_command('schtasks /create /xml "\\\\shots11\\tools\\scheduler\\lock.xml" /tn "\\UskoInc\\lock"')
        except Exception as E:
            print(E)



        # for c in const.command:
        #     try:
        #         _stdin, _stdout, _stderr = client.exec_command(c)
        #         out = _stdout.read().decode()
        #     except Exception as E:
        #         print(E)
        #     else:
        #         if out == '':
        #             # client.exec_command(r'reg add "HKCU\Software\Policies\Microsoft\Windows\System\Scripts\Logoff" /v "0" /t REG_SZ /d "C:\scripts\GPOUC\test.bat" /f')
        #             print(f'Create and enable schedule task {c[-2]}')
        #             client.exec_command(
        #                 f'schtasks /create /xml "\\\\shots11\\tools\\sendmetrics\\{c[-2]}.xml" /tn "\\UskoInc\\{c[-2]}"')
        #         else:
        #             print("Scheduled yet")

        cursor.close()
        connection.close()




# delete schedule tasks
# schtasks /end /tn "\UskoInc\1"
# schtasks /delete /tn "\UskoInc\1" /f


if __name__ == "__main__":
    main()



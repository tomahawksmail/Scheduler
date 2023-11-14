import paramiko
import re
import os
from dotenv import load_dotenv
import pymysql
import const

load_dotenv()

connection = pymysql.connect(host=os.environ.get('DBHOST'),
                             user=os.environ.get('DBUSER'),
                             password=os.environ.get('DBPASSWORD'),
                             database=os.environ.get('DATABASE'))

# env

reg_file = const.reg_file
bat_file = const.bat_file

client = paramiko.client.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def getWhiteUsers():
    """get real local users from host"""
    _stdin, _stdout, _stderr = client.exec_command(r'dir /b C:\Users')
    userlist = [x for x in _stdout.read().decode().splitlines() if x not in const.blackusers]
    return userlist



def ApplyREGFile(getWhiteUsers, host):
    """apply reg-file for each user"""
    for user in getWhiteUsers():
        path = f"C:\\Users\\{user}\\NTUSER.DAT"

        client.exec_command(f'reg load HKU\\Usko {path}')
        client.exec_command(f'reg import {reg_file}')
        client.exec_command('reg unload HKU\\Usko')

        SQLrequestSelect = """SELECT * from metricsStatus where hostname = %s and username = %s"""
        SQLrequestInsert = """INSERT INTO metricsStatus (`hostname`, `username`, `task1stamp`,
                                                        `task2stamp`, `task3stamp`) VALUES (
										                         %s, %s, NOW(), NOW(), NOW()) """
        try:
            connection.connect()
        except Exception as E:
            print(E)
        else:
            with connection.cursor() as cursor:
                cursor.execute(SQLrequestSelect, (host, user))
            result = cursor.fetchone()
            if result is None:
                with connection.cursor() as cursor:
                    cursor.execute(SQLrequestInsert, (host, user))
                connection.commit()

            cursor.close()
            connection.close()


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
        cursor.close()
        connection.close()

    for host in result:
        client.connect(host[0], username=os.environ.get('USER'), password=os.environ.get('PASSWORD'))

        # append QB system users to filter their
        const.blackusers.append(re.compile(r'QBDataServiceUser').match(r'dir /b C:\Users'))

        # copy GPO bat file
        client.exec_command(
            r"xcopy \\shots11\tools\sendmetrics\send_logoff.bat C:\WINDOWS\System32\GroupPolicy\User\Scripts\Logoff\ ")

        ApplyREGFile(getWhiteUsers, host)

        for c in const.command:
            try:
                _stdin, _stdout, _stderr = client.exec_command(c)
                out = _stdout.read().decode()
            except Exception as E:
                print(E)
            else:
                if out == '':
                    print(f'Create and enable schedule task {c[-2]}')
                    client.exec_command(
                        f'schtasks /create /xml "\\\\shots11\\tools\\sendmetrics\\{c[-2]}.xml" /tn "\\UskoInc\\{c[-2]}"')
                else:
                    print("Scheduled yet")





# delete schedule tasks
# schtasks /end /tn "\UskoInc\1"
# schtasks /delete /tn "\UskoInc\1" /f


if __name__ == "__main__":
    main()

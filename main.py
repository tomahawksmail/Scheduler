import paramiko
import re
import os
from dotenv import load_dotenv
import pymysql

load_dotenv()

connection = pymysql.connect(host=os.environ.get('DBHOST'),
                             user=os.environ.get('DBUSER'),
                             password=os.environ.get('DBPASSWORD'),
                             database=os.environ.get('DATABASE'))


# env
host = "USKO-ittest"
reg_file = "\\\\shots11\\tools\\sendmetrics\\gpologoff.reg"
bat_file = "C:\\WINDOWS\\System32\\GroupPolicy\\User\\Scripts\\Logoff\\"
# get schedule tasks
command1 = r'schtasks /query /tn "\UskoInc\1"'
command2 = r'schtasks /query /tn "\UskoInc\2"'
command3 = r'schtasks /query /tn "\UskoInc\3"'
command4 = r'schtasks /query /tn "\UskoInc\4"'
command = [command1, command2, command3, command4]


blackusers = ['NTUSER.DAT', 'Public', 'cpeter', 'Guest', 'DefaultAccount', 'skhashimi', 'mtsybulskyi',
              'Admin', 'Administrator', 'admin', 'sshd', 'DefaultAccount', 'WDAGUtilityAccount', 'QBPOSDBSrvUser',
              'WDAGUtilityAccount', 'DevToolsUser']


client = paramiko.client.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=os.environ.get('USER'), password=os.environ.get('PASSWORD'))

# append QB system users to filter their
blackusers.append(re.compile(r'QBDataServiceUser').match(r'dir /b C:\Users'))

# copy GPO bat file
client.exec_command(r"xcopy \\shots11\tools\sendmetrics\send_logoff.bat C:\WINDOWS\System32\GroupPolicy\User\Scripts\Logoff\ ")

# get real local users from host
def getWhiteUsers():
    _stdin, _stdout, _stderr = client.exec_command(r'dir /b C:\Users')
    userlist = [x for x in _stdout.read().decode().splitlines() if x not in blackusers]
    return userlist

# apply reg-file for each user
def ApplyREGFile(getWhiteUsers):

    for user in getWhiteUsers():
        path = f"C:\\Users\\{user}\\NTUSER.DAT"

        client.exec_command(f'reg load HKU\\Usko {path}')
        client.exec_command(f'reg import {reg_file}')
        client.exec_command('reg unload HKU\\Usko')

        SQLrequest = """SELECT * from metricsStatus where hostname = %s and username = %s"""
        try:
            connection.connect()
        except Exception as E:
            print(E)
        else:
            with connection.cursor() as cursor:
                cursor.execute(SQLrequest, (host, user))
            result = cursor.fetchall()
            print(result)
            cursor.close()
            connection.close()



ApplyREGFile(getWhiteUsers)

# for c in command:
#     try:
#         _stdin, _stdout, _stderr = client.exec_command(c)
#         out = _stdout.read().decode()
#     except Exception as E:
#         print(E)
#     else:
#         if out == '':
#             print(f'Create and enable schedule task {c[-2]}')
#             client.exec_command(f'schtasks /create /xml "\\\\shots11\\tools\\sendmetrics\\{c[-2]}.xml" /tn "\\UskoInc\\{c[-2]}"')
#         else:
#             print("Scheduled yet")




client.close()


# delete schedule tasks
#schtasks /end /tn "\UskoInc\1"
#schtasks /delete /tn "\UskoInc\1" /f
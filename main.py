import paramiko
import os
import time
from dotenv import load_dotenv
import pymysql

load_dotenv()
dir = "\\\\USKO-1125\Share"
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
        else:
            try:
                # get admin SID
                stdin_, stdout_, stderr_ = client.exec_command("wmic useraccount get SID", get_pty=True)
                stdout_.channel.set_combine_stderr(True)
                output = stdout_.readlines()
                SID = output[1].strip()[-45:]
                print('get admins SID', SID)

                print("create localdisconnect.xml")
                time.sleep(0.1)
                localdisconnect = f"""<?xml version="1.0" encoding="UTF-16"?>
                <Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
                  <RegistrationInfo>
                    <Date>2023-11-16T13:36:06.6388676</Date>
                    <Author>{host[0]}\\admin</Author>
                    <URI>\\USKO\local.disconnect</URI>
                  </RegistrationInfo>
                  <Triggers>
                    <SessionStateChangeTrigger>
                      <Enabled>true</Enabled>
                      <StateChange>ConsoleDisconnect</StateChange>
                    </SessionStateChangeTrigger>
                  </Triggers>
                  <Principals>
                    <Principal id="Author">
                      <UserId>{SID}</UserId>
                      <LogonType>InteractiveToken</LogonType>
                      <RunLevel>LeastPrivilege</RunLevel>
                    </Principal>
                  </Principals>
                  <Settings>
                    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
                    <DisallowStartIfOnBatteries>true</DisallowStartIfOnBatteries>
                    <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>
                    <AllowHardTerminate>true</AllowHardTerminate>
                    <StartWhenAvailable>false</StartWhenAvailable>
                    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
                    <IdleSettings>
                      <StopOnIdleEnd>true</StopOnIdleEnd>
                      <RestartOnIdle>false</RestartOnIdle>
                    </IdleSettings>
                    <AllowStartOnDemand>true</AllowStartOnDemand>
                    <Enabled>true</Enabled>
                    <Hidden>false</Hidden>
                    <RunOnlyIfIdle>false</RunOnlyIfIdle>
                    <WakeToRun>false</WakeToRun>
                    <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>
                    <Priority>7</Priority>
                  </Settings>
                  <Actions Context="Author">
                    <Exec>
                      <Command>C:\Windows\System32\GroupPolicy\Scheduler\localdisconnect.bat</Command>
                    </Exec>
                  </Actions>
                </Task>
                """

                print("create rdpdisconnect.xml")
                time.sleep(0.1)
                rdpdisconnect = f"""<?xml version="1.0" encoding="UTF-16"?>
    <Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
      <RegistrationInfo>
        <Date>2023-11-15T10:45:25.2169032</Date>
        <Author>{host[0]}\\admin</Author>
        <URI>\\USKO\\rdp.disconnect</URI>
      </RegistrationInfo>
      <Triggers>
        <SessionStateChangeTrigger>
          <Enabled>true</Enabled>
          <StateChange>RemoteDisconnect</StateChange>
        </SessionStateChangeTrigger>
      </Triggers>
      <Principals>
        <Principal id="Author">
          <UserId>{SID}</UserId>
          <LogonType>InteractiveToken</LogonType>
          <RunLevel>LeastPrivilege</RunLevel>
        </Principal>
      </Principals>
      <Settings>
        <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
        <DisallowStartIfOnBatteries>true</DisallowStartIfOnBatteries>
        <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>
        <AllowHardTerminate>true</AllowHardTerminate>
        <StartWhenAvailable>false</StartWhenAvailable>
        <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
        <IdleSettings>
          <StopOnIdleEnd>true</StopOnIdleEnd>
          <RestartOnIdle>false</RestartOnIdle>
        </IdleSettings>
        <AllowStartOnDemand>true</AllowStartOnDemand>
        <Enabled>true</Enabled>
        <Hidden>false</Hidden>
        <RunOnlyIfIdle>false</RunOnlyIfIdle>
        <WakeToRun>false</WakeToRun>
        <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>
        <Priority>7</Priority>
      </Settings>
      <Actions Context="Author">
        <Exec>
          <Command>C:\Windows\System32\GroupPolicy\Scheduler\rdpdisconnect.bat</Command>
        </Exec>
      </Actions>
    </Task>"""
                # said = 1192 \\USKO-1125\Share


                fullpath_localdisconnect = os.path.join(dir, 'localdisconnect' + ".xml")
                fullpath_rdpdisconnect = os.path.join(dir, 'rdpdisconnect' + ".xml")
                print(fullpath_localdisconnect)

                # Safe file
                with open(fullpath_localdisconnect, "w", encoding='utf-16') as f:
                    print(localdisconnect, file=f)

                with open(fullpath_rdpdisconnect, "w", encoding='utf-16') as f:
                    print(rdpdisconnect, file=f)


                print(f"Set timezone at {host[0]}")
                # set timezone
                client.exec_command(r'tzutil /s "Pacific Standard Time"')

                # Copy scripts
                command = "xcopy " + dir + r" C:\Scheduler\ /E /H /C /I /Y "
                client.exec_command(command)
                time.sleep(0.1)
                command = "xcopy " + dir + r" C:\Windows\System32\GroupPolicy\Scheduler\ /E /H /C /I /Y "
                client.exec_command(command)
                time.sleep(0.1)

                print(f"Deleting files from {host[0]}")
                client.exec_command(
                    r"rd C:\Scripts\ /S /Q")


                # Clear all old tasks
                print(f"Stoping schedule tasks at {host[0]}")
                client.exec_command(r'schtasks /end /tn  "\UskoInc\local.disconnect"')
                client.exec_command(r'schtasks /end /tn  "\UskoInc\rdp.disconnect"')
                client.exec_command(r'schtasks /end /tn  "\UskoInc\lockPC"')
                client.exec_command(r'schtasks /end /tn  "\UskoInc\logon"')
                client.exec_command(r'schtasks /end /tn  "\UskoInc\unlockPC"')
                #
                print(f"Deleting schedule tasks at {host[0]}")
                client.exec_command(r'schtasks /delete /tn  "\UskoInc\local.disconnect" /F')
                client.exec_command(r'schtasks /delete /tn  "\UskoInc\rdp.disconnect" /F')
                client.exec_command(r'schtasks /delete /tn  "\UskoInc\lockPC" /F')
                client.exec_command(r'schtasks /delete /tn  "\UskoInc\logon" /F')
                client.exec_command(r'schtasks /delete /tn  "\UskoInc\unlockPC" /F')
                #
                # Applying schedule tasks
                print(f"Applying schedule tasks at {host[0]}")
                client.exec_command(
                    r'schtasks /create /xml "C:\Windows\System32\GroupPolicy\Scheduler\localdisconnect.xml" /tn "\UskoInc\local.disconnect"')
                client.exec_command(
                    r'schtasks /create /xml "C:\Windows\System32\GroupPolicy\Scheduler\rdpdisconnect.xml" /tn "\UskoInc\rdp.disconnect"')













                # # Copy scripts for Shutdown and startup events
                # print(f"Copy scripts for Shutdown and startup events at {host[0]}")
                # client.exec_command(
                #     r"xcopy \\shots11\tools\sendmetrics\GroupPolicy\Machine\Scripts\ C:\Scripts\ /E /H /C /I /Y")
                # time.sleep(0.1)
                # client.exec_command(
                #     r"xcopy C:\Scripts\ C:\Windows\System32\GroupPolicy\Machine\Scripts\ /E /H /C /I /Y")
                # time.sleep(0.1)
                # print(f"Deleting files from {host[0]}")
                # client.exec_command(
                #     r"rd C:\Scripts\ /S /Q")
                # time.sleep(0.5)
                #
                # # Copy scripts for Logoff and Logon events /S /Q /Y /F /H /E /V /-Y /R
                # print(f"Copy scripts for Logoff and Logon events at {host[0]}")
                # client.exec_command(
                #     r"xcopy \\shots11\tools\sendmetrics\GroupPolicy\User\Scripts\ C:\Scripts\ /E /H /C /I /Y ")
                # time.sleep(0.1)
                # client.exec_command(
                #     r"xcopy C:\Scripts\ C:\Windows\System32\GroupPolicy\User\Scripts\ /E /H /C /I /Y ")
                # time.sleep(0.1)
                # print(f"Deleting files from {host[0]}")
                # client.exec_command(
                #     r"rd C:\Scripts\ /S /Q")
                #
                # # Copy scripts and xml for import schedule tasks
                # print(f"Copy scripts and xml for import schedule tasks at {host[0]}")
                # client.exec_command(
                #     r"xcopy \\shots11\tools\sendmetrics\GroupPolicy\Scheduler\ C:\Scheduler\ /E /H /C /I /Y ")
                # time.sleep(0.1)
                # client.exec_command(
                #     r"xcopy C:\Scheduler\ C:\Windows\System32\GroupPolicy\Scheduler\ /E /H /C /I /Y ")
                # print("-")
                # print("--")
                # print("---")
                # print("")

                #
                # print(f"Applying schedule tasks at {host[0]}")
                # client.exec_command(
                #     r'schtasks /create /xml "C:\Scheduler\local.disconnect.xml" /tn "\UskoInc\local.disconnect"')
                # client.exec_command(r'schtasks /create /xml "C:\Scheduler\lock.xml" /tn "\UskoInc\lockPC"')
                # client.exec_command(r'schtasks /create /xml "C:\Scheduler\logon.xml" /tn "\UskoInc\logon"')
                # client.exec_command(
                #     r'schtasks /create /xml "C:\Scheduler\rdp.disconnect.xml" /tn "\UskoInc\rdp.disconnect"')
                # client.exec_command(r'schtasks /create /xml "C:\Scheduler\unlock.xml" /tn "\UskoInc\unlockPC"')
                # time.sleep(0.5)
                #

                # print(f"Reboot host {host[0]}")
                # time.sleep(0.5)
                # client.exec_command(r"shutdown /r /t 00")


            except Exception as E:
                print(E)

        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()

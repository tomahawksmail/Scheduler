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
                    SID = output[1].strip()[-46:]
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
                              <Command>C:\Windows\System32\GroupPolicy\\tasks\localdisconnect.bat</Command>
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
                  <Command>C:\Windows\System32\GroupPolicy\\tasks\\rdpdisconnect.bat</Command>
                </Exec>
              </Actions>
            </Task>"""

                    print("create lock.xml")
                    time.sleep(0.1)
                    lock = f"""<?xml version="1.0" encoding="UTF-16"?>
        <Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
          <RegistrationInfo>
            <Date>2023-08-02T10:32:18.4689913</Date>
            <Author>{host[0]}\\admin</Author>
            <URI>\\USKO\lock</URI>
          </RegistrationInfo>
          <Triggers>
            <SessionStateChangeTrigger>
              <Enabled>true</Enabled>
              <StateChange>SessionLock</StateChange>
            </SessionStateChangeTrigger>
          </Triggers>
          <Principals>
            <Principal id="Author">
              <UserId>{SID}</UserId>
              <RunLevel>LeastPrivilege</RunLevel>
            </Principal>
          </Principals>
          <Settings>
            <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
            <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
            <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
            <AllowHardTerminate>true</AllowHardTerminate>
            <StartWhenAvailable>false</StartWhenAvailable>
            <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
            <IdleSettings>
              <StopOnIdleEnd>true</StopOnIdleEnd>
              <RestartOnIdle>false</RestartOnIdle>
            </IdleSettings>
            <AllowStartOnDemand>true</AllowStartOnDemand>
            <Enabled>true</Enabled>
            <Hidden>true</Hidden>
            <RunOnlyIfIdle>false</RunOnlyIfIdle>
            <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
            <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
            <WakeToRun>false</WakeToRun>
            <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>
            <Priority>7</Priority>
          </Settings>
          <Actions Context="Author">
            <Exec>
              <Command>C:\Windows\System32\GroupPolicy\\tasks\send_lock.bat</Command>
              <WorkingDirectory>C:</WorkingDirectory>
            </Exec>
          </Actions>
        </Task>"""

                    print("create logon.xml")
                    time.sleep(0.1)
                    logon = f"""<?xml version="1.0" encoding="UTF-16"?>
        <Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
          <RegistrationInfo>
            <Date>2023-10-10T17:04:38.7525536</Date>
            <Author>{host[0]}\\admin</Author>
            <URI>\\USKO\logon</URI>
          </RegistrationInfo>
          <Triggers>
            <LogonTrigger>
              <Enabled>true</Enabled>
            </LogonTrigger>
          </Triggers>
          <Principals>
            <Principal id="Author">
              <UserId>{SID}</UserId>
              <RunLevel>LeastPrivilege</RunLevel>
            </Principal>
          </Principals>
          <Settings>
            <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
            <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
            <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>
            <AllowHardTerminate>true</AllowHardTerminate>
            <StartWhenAvailable>false</StartWhenAvailable>
            <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
            <IdleSettings>
              <StopOnIdleEnd>true</StopOnIdleEnd>
              <RestartOnIdle>false</RestartOnIdle>
            </IdleSettings>
            <AllowStartOnDemand>true</AllowStartOnDemand>
            <Enabled>true</Enabled>
            <Hidden>true</Hidden>
            <RunOnlyIfIdle>false</RunOnlyIfIdle>
            <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
            <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
            <WakeToRun>false</WakeToRun>
            <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>
            <Priority>7</Priority>
          </Settings>
          <Actions Context="Author">
            <Exec>
              <Command>C:\Windows\System32\GroupPolicy\\tasks\send_logon.bat</Command>
            </Exec>
          </Actions>
        </Task>"""

                    print("create unlock.xml")
                    time.sleep(0.1)
                    unlock = f"""<?xml version="1.0" encoding="UTF-16"?>
        <Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
          <RegistrationInfo>
            <Date>2023-08-02T10:33:32.6403874</Date>
            <Author>{host[0]}\\admin</Author>
            <URI>\\USKO\\unlock</URI>
          </RegistrationInfo>
          <Triggers>
            <SessionStateChangeTrigger>
              <Enabled>true</Enabled>
              <StateChange>SessionUnlock</StateChange>
            </SessionStateChangeTrigger>
          </Triggers>
          <Principals>
            <Principal id="Author">
              <GroupId>S-1-5-32-545</GroupId>
              <RunLevel>LeastPrivilege</RunLevel>
            </Principal>
          </Principals>
          <Settings>
            <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
            <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
            <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
            <AllowHardTerminate>true</AllowHardTerminate>
            <StartWhenAvailable>false</StartWhenAvailable>
            <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
            <IdleSettings>
              <StopOnIdleEnd>true</StopOnIdleEnd>
              <RestartOnIdle>false</RestartOnIdle>
            </IdleSettings>
            <AllowStartOnDemand>true</AllowStartOnDemand>
            <Enabled>true</Enabled>
            <Hidden>true</Hidden>
            <RunOnlyIfIdle>false</RunOnlyIfIdle>
            <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
            <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
            <WakeToRun>false</WakeToRun>
            <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>
            <Priority>7</Priority>
          </Settings>
          <Actions Context="Author">
            <Exec>
              <Command>C:\Windows\System32\GroupPolicy\\tasks\send_unlock.bat</Command>
              <WorkingDirectory>C:</WorkingDirectory>
            </Exec>
          </Actions>
        </Task>"""


                    print(f"Deleting template files from share folder")

                    client.exec_command(
                        f"rd {dir}\\templates /S /Q")


                    print(f"Generating personal files for {host[0]}...")
                    fullpath_localdisconnect = os.path.join(dir + "/templates", 'localdisconnect' + ".xml")
                    fullpath_rdpdisconnect = os.path.join(dir + "/templates", 'rdpdisconnect' + ".xml")
                    fullpath_lock = os.path.join(dir + "/templates", 'lock' + ".xml")
                    fullpath_logon = os.path.join(dir + "/templates", 'logon' + ".xml")
                    fullpath_unlock = os.path.join(dir + "/templates", 'unlock' + ".xml")

                    # Safe file
                    with open(fullpath_localdisconnect, "w", encoding='utf-16') as f:
                        print(localdisconnect, file=f)

                    with open(fullpath_rdpdisconnect, "w", encoding='utf-16') as f:
                        print(rdpdisconnect, file=f)

                    with open(fullpath_lock, "w", encoding='utf-16') as f:
                        print(lock, file=f)

                    with open(fullpath_logon, "w", encoding='utf-16') as f:
                        print(logon, file=f)

                    with open(fullpath_unlock, "w", encoding='utf-16') as f:
                        print(unlock, file=f)

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
                    command = "xcopy " + dir + "\GroupPolicy\\Machine" + r" C:\Windows\System32\GroupPolicy\Machine /E /H /C /I /Y /O"
                    client.exec_command(command)
                    command = "xcopy " + dir + "\GroupPolicy\\User" +    r" C:\Windows\System32\GroupPolicy\User /E /H /C /I /Y /O"
                    client.exec_command(command)

                    # Set Permissions
                    command = "takeown /F C:\Windows\System32\GroupPolicy\Machine\Scripts\Startup\startup.bat /A"
                    client.exec_command(command)
                    command = r'icacls C:\Windows\System32\GroupPolicy\Machine\Scripts\Startup\startup.bat /setowner "NT AUTHORITY\SYSTEM"'
                    client.exec_command(command)
                    command = "takeown /F C:\Windows\System32\GroupPolicy\\User\Scripts\Logoff\send_logoff.bat /A"
                    client.exec_command(command)
                    command = r'icacls C:\Windows\System32\GroupPolicy\\User\Scripts\Logoff\send_logoff.bat /setowner "NT AUTHORITY\SYSTEM"'
                    client.exec_command(command)

                    command = "xcopy " + dir + r"\tasks" + r" C:\Windows\System32\GroupPolicy\tasks /E /H /C /I /Y /O"
                    client.exec_command(command)

                    command = "xcopy " + dir + r"\templates" + r" C:\Windows\System32\GroupPolicy\tasks /E /H /C /I /Y "
                    client.exec_command(command)
                    time.sleep(0.1)




                    # Clear all old tasks
                    print(f"Stoping schedule tasks at {host[0]}")
                    print("....................................")
                    client.exec_command(r'schtasks /end /tn  "\UskoInc\local.disconnect"')
                    client.exec_command(r'schtasks /end /tn  "\UskoInc\rdp.disconnect"')
                    client.exec_command(r'schtasks /end /tn  "\UskoInc\lockPC"')
                    client.exec_command(r'schtasks /end /tn  "\UskoInc\logon"')
                    client.exec_command(r'schtasks /end /tn  "\UskoInc\unlockPC"')
                    #
                    print(f"Deleting schedule tasks at {host[0]}")
                    print("....................................")
                    client.exec_command(r'schtasks /delete /tn  "\UskoInc\local.disconnect" /F')
                    client.exec_command(r'schtasks /delete /tn  "\UskoInc\rdp.disconnect" /F')
                    client.exec_command(r'schtasks /delete /tn  "\UskoInc\lockPC" /F')
                    client.exec_command(r'schtasks /delete /tn  "\UskoInc\logon" /F')
                    client.exec_command(r'schtasks /delete /tn  "\UskoInc\unlockPC" /F')

                    # Applying schedule tasks
                    print(f"Applying schedule tasks at {host[0]}")
                    print("....................................")
                    client.exec_command(
                        r'schtasks /create /xml "C:\Windows\System32\GroupPolicy\tasks\localdisconnect.xml" /tn "\UskoInc\local.disconnect"')
                    client.exec_command(
                        r'schtasks /create /xml "C:\Windows\System32\GroupPolicy\tasks\rdpdisconnect.xml" /tn "\UskoInc\rdp.disconnect"')
                    client.exec_command(
                        r'schtasks /create /xml "C:\Windows\System32\GroupPolicy\tasks\lock.xml" /tn "\UskoInc\lock"')
                    client.exec_command(
                        r'schtasks /create /xml "C:\Windows\System32\GroupPolicy\tasks\logon.xml" /tn "\UskoInc\logon"')
                    client.exec_command(
                        r'schtasks /create /xml "C:\Windows\System32\GroupPolicy\tasks\unlock.xml" /tn "\UskoInc\unlock"')





                    print(f"Reboot host {host[0]}")
                    time.sleep(0.5)
                    client.exec_command(r"shutdown /r /t 00")


                except Exception as E:
                    print(E)

        cursor.close()
        connection.close()




if __name__ == "__main__":
    main()

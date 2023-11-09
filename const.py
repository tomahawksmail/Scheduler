reg_file = "\\\\shots11\\tools\\sendmetrics\\gpologoff.reg"
bat_file = "C:\\WINDOWS\\System32\\GroupPolicy\\User\\Scripts\\Logoff\\"
bat      = f'\\shots11\tools\sendmetrics\send_logoff.bat'

command1 = r'schtasks /query /tn "\UskoInc\1"'
command2 = r'schtasks /query /tn "\UskoInc\2"'
command3 = r'schtasks /query /tn "\UskoInc\3"'
command = [command1, command2, command3]
echo off
set host=%Computername%
set "url=https://ifconfig.me/"
curl %url% > C:\Users\%username%\AppData\Local\temp_ip.txt
set /p "public_ip=" < C:\Users\%username%\AppData\Local\temp_ip.txt
del C:\Users\%username%\AppData\Local\temp_ip.txt

set name=%username%
set tm=%date:~4,2%/%date:~7,2%/%date:~10,4%-%time: =%
set event=local.disconnect

set result=http://192.168.24.10/sendmetrics?host=%host%^&public_ip=%public_ip%^&name=%name%^&tm=%tm%^&event=%event%
curl -X GET "%result%"




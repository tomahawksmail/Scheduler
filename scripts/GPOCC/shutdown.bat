echo off
set host=%Computername%
set public_ip=
set name=
set tm=%date:~4,2%/%date:~7,2%/%date:~10,4%-%time: =%
set event=shutdown

set result=http://192.168.24.10/sendmetrics?host=%host%^&public_ip=%public_ip%^&name=%name%^&tm=%tm%^&event=%event%
curl -X GET "%result%"




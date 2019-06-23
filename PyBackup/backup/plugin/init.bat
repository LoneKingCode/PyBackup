@echo off
pip3 install --upgrade pip
pip3 install oss2 cos-python-sdk-v5

schtasks /create /tn "backup_web_db" /ru system /tr "python d:/AutoBackup/backup.py" /sc DAILY /st 01:00

start %systemroot%\tasks

echo 创建计划任务成功，请检查...

pause
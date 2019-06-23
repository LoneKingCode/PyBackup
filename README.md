# PyBackup
> 自动备份目录和数据库


可以备份本地目录及数据库(mysql,mssql)，和远程FTP目录及远程数据库(mysql,mssql),

同步备份文件到Ftp,阿里云Oss,腾讯云Cos,OneDrive,Email,还有本地，并删除指定天数的旧备份文件，

支持忽略文件，目录，后缀，email压缩包分卷发送规避邮箱附件大小限制


### 需要的环境
```
python3以及库oss2和cos-python-sdk-v5
windows上需要7z.exe，mysqldump.exe,SQLCMD.exe,SQLCMD.rll 在本程序plugins目录已中自带有无需下载
linux上需要安装p7zip(确保7za命令可以执行),mysqldump是安装mysql时附带的,sqlcmd这个是mssql的命令行工具,linux上也有https://docs.microsoft.com/zh-cn/sql/linux/sql-server-linux-setup-tools?view=sql-server-2017 暂
如果以下一键包安装出现问题，在安装python3成功后自行安装依赖库
pip3 install --upgrade pip
pip3 install oss2 cos-python-sdk-v5
```
### 安装
Linux

```sh
wget --no-check-certificate https://raw.githubusercontent.com/LoneKingCode/PyBackup/master/PyBackup/backup/plugin/init.sh -O pybackup.sh && bash pybackup.sh
执行完本程序存放在脚本同目录
安装完输入python3 -h 和pip3 -h  还有7za 查看结果 判断是否安装成功，同时需要mysqldump命令
然后自行设置计划任务 使用crontab或者web面板内自带计划
本程序目录/plugin/cron.sh为使用crontab设置计划任务 自行修改里面路径后执行sh cron.sh 即可
backup.py为主程序 设置的命令为 python3 yourPath/backup.py
```


Windows

```sh
首先下载安装python3.6.3 https://www.python.org/ftp/python/3.6.3/python-3.6.3.exe
安装完命令提示符中输入python3 -h 和pip3 -h 命令看结果 判断是否安装成功
然后下载本程序并解压 https://github.com/LoneKingCode/PyBackup/archive/master.zip
然后修改本程序目录中/backup/plugin/init.bat 批处理文件中这一行命令
schtasks /create /tn "backup_web_db" /ru system /tr "python /yourPath/backup.py" /sc DAILY /st 01:00
修改backup_web_db为计划任务名称,修改yourPath为文件实际位置,DATLY为每日,01:00 凌晨一点执行
想计划为其他周期自行百度schtasks或者windows添加计划任务
修改完成保存后 双击 init.bat运行即可
init.bat作用是安装python3依赖库及设置计划任务
```

## 使用方法
提前说下:
```
配置文件中[]为数组，内部元素用,来隔开
{'key':'value','key':'value'}为字典 
所有[{}] 这种结构的都可以设置为[{},{},{},]多个配置
```
参考注释修改config.py中配置

### onedrive认证方法
```
修改config.py中配置后，程序目录运行python3 auth_onedrive.py
```
![](https://i.loli.net/2019/02/06/5c5a90ad4f540.png) 
![](https://i.loli.net/2019/02/06/5c5a909812f68.png) 

```
backup.py为主程序 如果要设置计划任务 设置为 python3 yourPath/backup.py
```

## 更新历史
* 2019.6.23  
         1.添加忽略文件，目录，后缀  
         2.设置ftp的被动/主动模式  
         3.支持email分卷
## 关于作者

LoneKing – [@LoneKing's Blog](https://loneking.net) 


[https://github.com/LoneKingCode/PyBackup](https://github.com/LoneKingCode/PyBackup)


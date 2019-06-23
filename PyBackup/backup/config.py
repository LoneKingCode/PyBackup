import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

#备份的站点目录
#type: local,ftp local(本地),ftp(远程站点备份)
#path: 要备份的目录
#archive_type: 7z,zip,tar(7zip支持的类型)
#archive_password: 压缩包密码
#type为ftp时需要额外配置: host:FTP服务器地址 port:端口 username:用户名 password:密码
#ignoreFile: 忽略文件名
#ignoreDir: 忽略文件夹名
#ignoreExt: 忽略后缀
#pasv: ftp的模式 0主动模式 1 #被动模式
SITES = [{ 'type':'local','path':'D:\\wwwroot\\www.aa.com','ignore_dir':['dir'],'ignore_ext':['txt'],'ignore_file':['asd.txt'],
         'archive_type':'zip','archive_password':'123' },
         {  'type':'ftp', 'path':'/WEB',  'archive_type':'zip','archive_password':'123',
          'host':'yourFtpUrl','port':21,'username':'yourFtpUsername','password':'yourFtpPwd','pasv':0}]

#备份的数据库
#type: 数据库类型 mssql,mysql
#database_name: 数据库名称
#username: 数据库用户名
#password: 数据库密码
#host: 数据库服务器地址 为空代表本地
#port: 数据库端口
#archive_type: 7z,zip,tar(7zip支持的类型)
#archive_password: 压缩包密码
#sqlcmd_path 或 mysqldump_path : mssql和mysql命令行工具路径 windows下无需修改 linux请设置为''
#***注意***
#设置备份远程数据库时 请在数据库中设置为备份机IP可连接或任意IP可连接(mysql添加用户且设置Host为%或指定IP)
#mysql
#linux如果mysqldump命令可以直接执行的话mysqldump设置为'',否则设置为实际路径,windows下设置mysqldump.exe位置,本程序plugin目录自带有(MYSQL5.7)
#mssql(Sql Server)
#linux确保SQLCMD命令可以直接执行的话sqlcmd_path设置为'',windows下设置SQLCMD.exe位置,本程序plugin目录自带有(SQLSERVER2014)
#命令行工具有需要可在plugin目录替换为你需要的版本
DATABASES = [{'type':'mssql','database_name':'yourDatabaseName','username':'sa','password':'123','host':'123.123.123.123','port':'1433',
              'archive_type':'zip','archive_password':'123','sqlcmd_path':os.path.join(str(ROOT_DIR),'plugin') + '\\SQLCMD.exe'},
            {'type':'mysql','database_name':'yourDatabaseName','username':'test','password':'asd','host':'aa.aa.com','port':'3306',
            'archive_type':'zip','archive_password':'123','mysqldump_path': os.path.join(str(ROOT_DIR),'plugin') + '\\mysqldump.exe'}]

#保留几天内的文件
KEEP_DAYS = 7

#本地备份文件保存位置
LOCAL_SAVE_PATH = {'sites':'D:\\Save\\backup\\sites','databases':'D:\\Save\\backup\\databases'}

#备份文件临时保存位置
TEMP_SAVE_PATH = 'D:\\Save\\backuptemp'

#远程备份类型 为空则只保存到本地
#可选 ftp,email,oss,cos,onedrive
#***注意***
#email的话注意附件大小 有的限制是25MB 有的是50MB
REMOTE_SAVE_TYPE = ['oss','cos','ftp','email','onedrive']

#备份出错尝试次数
ERROR_COUNT = 3

#FTP备份配置
#host: FTP服务器地址
#port: FTP端口
#username: FTP用户名
#password: FTP密码
#site_save_path: 站点备份文件保存的路径 确保路径已经存在
#db_save_path: 数据库备份文件保存的路径 确保路径已经存在
#pasv: ftp的模式 0主动模式 1 #被动模式
FTP_OPTIONS = [{'host':'yourFtpUrl','port':21,'username':'yourFtpUsername','password':'yourPwd',
                'site_save_path':'/backup/sites','db_save_path':'/backup/databases','pasv':0},]

#阿里云OSS配置
#sitedir: 站点备份文件保存目录
#databasedir: 数据库文件保存目录
#url:你oss地址
#bucket: 存储桶名称
#accesskeyid: AccessKeyId
#accesskeysecret : AccessKeySecret
OSS_OPTIONS = [{'sitedir':'sites','databasedir':'databases','url':'oss-xx-xxxx.aliyuncs.com','bucket':'bucketName',
                'accesskeyid':'ASDI123ISDD12','accesskeysecret':'SAD123ASD123ASD213ASD'},]

#腾讯云COS配置
#sitedir: 站点备份文件保存目录
#databasedir: 数据库文件保存目录
#region:区域
#bucket: 存储桶名称
#accesskeyid: AccessKeyId
#accesskeysecret : AccessKeySecret
COS_OPTIONS = [{'sitedir':'sites','databasedir':'databases','region':'ap-hongkong','bucket':'bucketName',
                'accesskeyid':'ASD123ASDASD123','accesskeysecret':'ASD123ASDASD123ASD'},]

#OneDrive配置
#name: 名称
#用于区别配置文件中配置，可以设置为多个{'name':'backup1'
#.....},{'name':'backup2'.....}，这样的话需要你认证多次不同账户
#sitedir: 站点备份文件保存目录
#databasedir: 数据库文件保存目录
ONE_DRIVE_OPTION = [{'name':'backup1','sitedir':'sites','databasedir':'databases',}]

#默认无需修改 用于申请API访问 此处采用萌咖(MoeClub)提供的
ONE_DRIVE_CLIENT = {'client_id':'ea2b36f6-b8ad-40be-bc0f-e5e4a4a7d4fa','client_secret':'h27zG8pr8BNsLU0JbBh5AOznNS5Of5Y540l/koc7048='}

#Email备份配置

#发送配置
#host: 邮箱smtp服务器地址
#username: 用户名 password:密码 port:端口 is_ssl:是否ssl加密连接 True或者False
#partSize: 分卷大小  因为有的邮箱限制附件大小 可以分卷发送 为''空则不分卷
EMAIL_OPTIONS_SENDERS = [{'host':'smtp.AA.com','username':'AA@AA.com','password':'123446','port':465,'is_ssl':True,'partSize':'2m','archive_type':'zip'},]

#接收邮箱
EMAIL_OPTIONS_RECEIVERS = ['receivebackup@foxmail.com',]

#7z.exe位置 利用7zip来压缩
#只有windows需要(在程序plugin目录中已经附带有了
#linux安装过"p7zip-full"就行
WINDOWS_7ZIP_PATH = os.path.join(str(ROOT_DIR),'plugin') + '\\7z.exe'
import os
import sys
import datetime
import subprocess
from  util.ftphelper import FtpHelper
from  util.emailhelper import EmailHelper
from  util.loghelper import LogHelper
from  util.filehelper import FileHelper
from  util.coshelper import CosHelper
from  util.osshelper import OssHelper
from  util.onedrivehelper import OneDriveHelper
from  config import *

def log(msg):
    print(msg)
    LogHelper.info(msg)

def get_datestr():
    return datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

def backup():
    if not os.path.exists(LOCAL_SAVE_PATH['sites']):
        log('本地站点备份文件保存位置不存在，尝试创建')
        try:
            os.makedirs(LOCAL_SAVE_PATH['sites'])
            log('创建成功:' + LOCAL_SAVE_PATH['sites'])
        except Exception as e:
            msg = '创建失败，失败原因:' + str(e)
            print(msg)
            log(msg)
            return
    if not os.path.exists(LOCAL_SAVE_PATH['databases']):
        log('本地数据库备份文件保存位置不存在，尝试创建')
        try:
            os.makedirs(LOCAL_SAVE_PATH['databases'])
            log('创建成功:' + LOCAL_SAVE_PATH['databases'])
        except Exception as e:
            print('创建失败，失败原因:' + str(e))
            log(msg)
            return
    if not os.path.exists(TEMP_SAVE_PATH):
        log('备份文件临时保存位置不存在，尝试创建')
        try:
            os.makedirs(TEMP_SAVE_PATH)
            log('创建成功:' + TEMP_SAVE_PATH)
        except Exception as e:
            print('创建失败，失败原因:' + str(e))
            log(msg)
            return

    site_files = backup_site()
    db_files = backup_db()
    remote_save(site_files,db_files)
    clear_old_backup()

#清除旧备份文件
def clear_old_backup():
    if 'ftp' in REMOTE_SAVE_TYPE:
        #清除远程FTP上旧备份文件
        for option in FTP_OPTIONS:
            ftp = FtpHelper(option['host'],option['username'], option['password'],option['port'],option['pasv'])

            for filename in ftp.get_files(option['site_save_path']):
                if is_oldfile(filename):
                    ftp.delete_file(option['site_save_path'],filename)

            for filename in ftp.get_files(option['db_save_path']):
                if is_oldfile(filename):
                    ftp.delete_file(option['db_save_path'],filename)
            ftp.quit()

    #清除本地网站旧文件
    for root, dirs, files in os.walk(LOCAL_SAVE_PATH['sites']):
            for filename in files:
                if is_oldfile(filename):
                    FileHelper.delete(os.path.join(root, filename))

    #清除本地数据库旧文件
    for root, dirs, files in os.walk(LOCAL_SAVE_PATH['databases']):
        for filename in files:
            if is_oldfile(filename):
                FileHelper.delete(os.path.join(root, filename))
    if 'oss' in REMOTE_SAVE_TYPE:
        #清除oss旧文件
        for option in OSS_OPTIONS:
            oss = OssHelper(option['accesskeyid'],option['accesskeysecret'],option['url'],option['bucket'])
            for file in oss.get_file_list(option['sitedir'].rstrip('/') + '/') + oss.get_file_list(option['databasedir'].rstrip('/') + '/'):
                if is_oldfile(os.path.basename(file)):
                    oss.delete(file)
    if 'css' in REMOTE_SAVE_TYPE:
        #清除cos旧文件
        for option in COS_OPTIONS:
            cos = CosHelper(option['accesskeyid'],option['accesskeysecret'],option['region'],option['bucket'])
            for file in cos.get_file_list(option['sitedir'].rstrip('/') + '/') + cos.get_file_list(option['databasedir'].rstrip('/') + '/'):
                if is_oldfile(os.path.basename(file)):
                    cos.delete(file)
    if 'onedrive' in REMOTE_SAVE_TYPE:
        #清除onedrive旧文件
        for option in ONE_DRIVE_OPTION:
            od = OneDriveHelper(option['name'])
            for file in od.get_file_list(option['sitedir'].rstrip('/') + '/'):
                if is_oldfile(os.path.basename(file['name'])):
                    od.delete(os.path.join(option['sitedir'],file['name']))
            for file in od.get_file_list(option['databasedir'].rstrip('/') + '/'):
                if is_oldfile(os.path.basename(file['name'])):
                    od.delete(os.path.join(option['databasedir'],file['name']))
    log('清除旧备份文件 完成')

#是否为旧文件
def is_oldfile(filename):
    try:
        filenames = filename.split('_')  #name_'%Y-%m-%d-%H-%M-%S.zip'
        filedatestr = filenames[1].split('-')[:6]
        filedatestr[5] = filedatestr[5].split('.')[0]
        filedatestr = '-'.join(filedatestr)
        filedate = datetime.datetime.strptime(filedatestr, '%Y-%m-%d-%H-%M-%S')
        keep_date = datetime.datetime.now() - datetime.timedelta(days=KEEP_DAYS)
        #如果文件日期在要保留的日期之前
        return filedate < keep_date
    except :
        return False

#远程保存
def remote_save(site_files,db_files):
    errcount=0
    for type in REMOTE_SAVE_TYPE:
        if type not in 'ftp,email,cos,oss,onedrive' or not type:
            log('远程保存配置类型"' + type + '"错误，应该为ftp,email,cos,oss,onedrive')
            continue
        while errcount < ERROR_COUNT:
            try:
                if type == 'ftp':
                    remote_save_ftp(site_files , db_files)
                elif type == 'email':
                    remote_save_email(site_files ,db_files)
                elif type == 'oss':
                    remote_save_oss(site_files,db_files)
                elif type == 'cos':
                    remote_save_cos(site_files,db_files)
                elif type == 'onedrive':
                    remote_save_onedrive(site_files,db_files)
                break
            except Exception as e:
                log(str(e))
                print(str(e))
                errcount = errcount + 1
                print('备份' + type + '方式第' + str(errcount) + '次出错')
    FileHelper.move_bulk(site_files,LOCAL_SAVE_PATH['sites'])
    FileHelper.move_bulk(db_files,LOCAL_SAVE_PATH['databases'])

#远程保存到onedrive
def remote_save_onedrive(site_files,db_files):
    log('开始上传到OneDrive')
    for option in ONE_DRIVE_OPTION:
        if not option:
            continue
        print('开始上传到:' + option['name'])
        od = OneDriveHelper(option['name'])
        for file in site_files:
            if not file:
                continue
            filename = os.path.basename(file)
            od.upload(option['sitedir'].rstrip('/') + '/' + filename,file)
        for file in db_files:
            if not file:
                continue
            filename = os.path.basename(file)
            od.upload(option['databasedir'].rstrip('/') + '/' + filename,file)
    log('远程保存到OneDrive 完成')

#远程保存到oss
def remote_save_oss(site_files,db_files):
    log('开始上传到oss')
    for option in OSS_OPTIONS:
        if not option:
            continue
        oss = OssHelper(option['accesskeyid'],option['accesskeysecret'],option['url'],option['bucket'])
        for file in site_files:
            if not file:
                continue
            filename = os.path.basename(file)
            oss.upload(option['sitedir'].rstrip('/') + '/' + filename,file)
        for file in db_files:
            if not file:
                continue
            filename = os.path.basename(file)
            oss.upload(option['databasedir'].rstrip('/') + '/' + filename,file)
    log('远程保存到oss 完成')


#远程保存到cos
def remote_save_cos(site_files,db_files):
    log('开始上传到cos')
    for option in COS_OPTIONS:
        if not option:
            continue
        cos = CosHelper(option['accesskeyid'],option['accesskeysecret'],option['region'],option['bucket'])
        for file in site_files:
            if not file:
                continue
            filename = os.path.basename(file)
            cos.upload(option['sitedir'].rstrip('/') + '/' + filename,file)
        for file in db_files:
            if not file:
                continue
            filename = os.path.basename(file)
            cos.upload(option['databasedir'].rstrip('/') + '/' + filename,file)
    log('远程保存到cos 完成')


#远程保存到ftp
def remote_save_ftp(site_files,db_files):
    log('开始上传到FTP')
    for option in FTP_OPTIONS:
        ftp = FtpHelper(option['host'],option['username'], option['password'],option['port'],option['pasv'])
        for file in site_files:
            if not file:
                continue
            filename = os.path.basename(file)
            ftp.upload_file(file,option['site_save_path'].rstrip('/') + '/' + filename)
        for file in db_files:
            if not file:
                continue
            filename = os.path.basename(file)
            ftp.upload_file(file,option['db_save_path'].rstrip('/') + '/' + filename)
        ftp.quit()
    log('远程保存到FTP 完成')


#远程发送到邮箱
def remote_save_email(site_files,db_files):
    log('开始发送到Email')
    for option in EMAIL_OPTIONS_SENDERS:
        email = EmailHelper(option['host'],option['username'],option['password'],option['port'],option['is_ssl'])
        for file in site_files:
            if not file:
                continue
            if option['partSize']:
                part_file_path = os.path.join(TEMP_SAVE_PATH,'EmailPart')
                if not os.path.exists(part_file_path):
                    os.makedirs(part_file_path)
                flag,msg = FileHelper.compress(option['archive_type'],file,part_file_path,os.path.basename(file),
                                       None,None,None,None,option['partSize'])
                part_files = FileHelper.get_file_list(part_file_path)
                for part_file in part_files:
                    flag,msg = email.send('新的站点备份','站点备份:' + os.path.basename(part_file),'站点备份:' + os.path.basename(part_file),EMAIL_OPTIONS_RECEIVERS,[part_file])
                FileHelper.delete(part_file_path)
            else:
                flag,msg = email.send('新的站点备份','站点备份:' + os.path.basename(file),'站点备份:' + os.path.basename(file),EMAIL_OPTIONS_RECEIVERS,[file])
            if flag:
                log('使用 {0} 发送邮件 {1} 成功'.format(option['username'],file))
            else:
                log('使用 {0} 发送邮件 {1} 失败，原因:'.format(option['username'],file,msg))
        
        for file in db_files:
            if not file:
                continue
            if option['partSize']:
                if not os.path.exists(part_file_path):
                   os.makedirs(part_file_path)
                part_file_path = os.path.join(TEMP_SAVE_PATH,'EmailPart')
                flag,msg = FileHelper.compress(option['archive_type'],file,part_file_path,os.path.basename(file),
                                       None,None,None,None,option['partSize'])
                part_files = FileHelper.get_file_list(part_file_path)
                for part_file in part_files:
                    flag,msg = email.send('新的数据库备份','数据库备份:' + os.path.basename(part_file),'数据库备份:' + os.path.basename(part_file),EMAIL_OPTIONS_RECEIVERS,[part_file])
                FileHelper.delete(part_file_path)
            else:
                flag,msg = email.send('新的数据库备份','数据库备份:' + os.path.basename(file),'数据库备份:' + os.path.basename(file),EMAIL_OPTIONS_RECEIVERS,[file])
            if flag:
                log('使用 {0} 发送邮件 {1} 成功'.format(option['username'],file))
            else:
                log('使用 {0} 发送邮件 {1} 失败，原因:'.format(option['username'],file,msg))
        email.quit()
    log('发送到Email 完成')

#备份站点
def backup_site():
    site_files = []
    log('开始备份站点')
    for site in SITES:
        if not site:
            continue
        site_path = site['path']
        if site['type'] == 'ftp':
            ftp = FtpHelper(site['host'],site['username'], site['password'],site['port'],site['pasv'])
            log('开始下载FTP远程目录:' + site['path'])
            ftp.download_dir(os.path.join(TEMP_SAVE_PATH ,os.path.basename(site['path'])),site['path'])
            log('下载FTP远程目录结束')
            site_path = os.path.join(TEMP_SAVE_PATH,os.path.basename(site['path']))
        archive_type = site['archive_type']
        if not os.path.exists(site_path):
            log('站点路径%s不存在' % site_path)
            continue
        if archive_type not in 'zip,tar,gztar':
            log('archive_type存档类型"' + archive_type + '"错误,应该为zip,tar,gztar')
            continue
        dirname = os.path.basename(site_path)
        site_filename = dirname + '_' + get_datestr()
        flag,msg = FileHelper.compress(archive_type,site_path,TEMP_SAVE_PATH,site_filename,
                                       site['archive_password'],site['ignore_dir'],site['ignore_ext'],site['ignore_file'])
        if site['type'] == 'ftp':
            FileHelper.delete(site_path)
        if not flag:
            log('创建' + site_path + '存档出错:' + msg)
            continue
        site_archive_path = msg
        site_files.append(site_archive_path)
    log('备份站点结束')
    return site_files

#备份数据库
def backup_db():
    db_files = []
    for db in DATABASES:
        if not db:
            continue
        db_type = db['type']
        if db_type not in 'mssql,mysql':
            log('type数据库类型错误,应该为mssql,mysql')
            continue
        log('备份数据库{0}:{1} 开始'.format(db_type,db['database_name']))
        if db_type == 'mysql':
            db_files.append(backup_db_mysql(db))
        elif db_type == 'mssql':
            db_files.append(backup_db_mssql(db))
        log('备份数据库{0}:{1} 结束'.format(db_type,db['database_name']))
    return db_files

#备份 mssql 数据库
def backup_db_mssql(db):
    db_filename = db['database_name'] + '_' + get_datestr() + '.bak'
    db_filepath = TEMP_SAVE_PATH + os.path.sep + db_filename
    archive_type = db['archive_type']
    if archive_type not in 'zip,tar,gztar':
        log('archive_type存档类型"' + archive_type + '"错误,应该为zip,tar,gztar')
        return None
    sqlcmd = 'sqlcmd' if not db['sqlcmd_path'] else db['sqlcmd_path']
    cmd = '{0} -S {1},{2} -U {3} -P {4} -Q "BACKUP DATABASE {5} to disk="{6}"'.format(sqlcmd,db['host'],db['port'],db['username'],db['password'],db['database_name'],db_filepath)
    status,result = subprocess.getstatusoutput(cmd)
    if status != 0:
        log('备份数据库{0}出错,返回值为{1},执行的命令为{2}'.format(db['database_name'],result,cmd))
        return None
    else:
        flag,msg = FileHelper.compress(archive_type,db_filepath,TEMP_SAVE_PATH,db_filename,db['archive_password'])
        archive_path = msg
        if flag:
            FileHelper.delete(db_filepath)
            return archive_path
        else:
            log('打包数据库文件出错,' + msg)
            return None


#备份 mysql 数据库
def backup_db_mysql(db):
    db_filename = db['database_name'] + '_' + get_datestr() + '.sql'
    db_filepath = TEMP_SAVE_PATH + os.path.sep + db_filename
    archive_type = db['archive_type']
    if archive_type not in 'zip,tar,gztar':
        log('archive_type存档类型"' + archive_type + '"错误,应该为zip,tar,gztar')
        return None
    host = '' if not db['host']  else   '-h ' + db['host']
    mysqldump = 'mysqldump' if not db['mysqldump_path'] else db['mysqldump_path']
    cmd = '{0} {1} -P{2} -u{3} -p{4} --databases {5} > {6}'.format(mysqldump,host,db['port'],db['username'],db['password'],db['database_name'],db_filepath)
    status,result = subprocess.getstatusoutput(cmd)
    if status != 0:
        log('备份数据库{0}出错,返回值为{1},执行的命令为{2}'.format(db['database_name'],result,cmd))
        return None
    else:
        flag,msg = FileHelper.compress(archive_type,db_filepath,TEMP_SAVE_PATH,db_filename,db['archive_password'])
        archive_path = msg
        if flag:
            FileHelper.delete(db_filepath)
            return archive_path
        else:
            log('打包数据库文件出错,' + msg)
            return None


def start():
    starttime = datetime.datetime.now()
    log('开始备份')
    try:
        backup()
    except Exception as e:
        log('哎呀 出错了:' + str(e))
    endtime = datetime.datetime.now()
    log('本次备份完成，耗时{0}秒'.format((endtime - starttime).seconds))

if __name__ == '__main__':
    start()

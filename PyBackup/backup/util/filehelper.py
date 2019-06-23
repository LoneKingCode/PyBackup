import os
import shutil
import time
import zipfile
import tarfile
import subprocess
import platform
import json
from util.stringhelper import StringHelper
from config import WINDOWS_7ZIP_PATH


class FileHelper(object):
    @staticmethod
    def get_file_list(path):
        filelist=[]
        for root,dir,files in os.walk(path):
            for file in files:
                fullpath = os.path.join(root,file)
                filelist.append(fullpath)
        return filelist
    @staticmethod
    def open_json(filepath):
        with open(filepath,'r') as f:
            try:
                data = json.load(f)
                return data
            except Exception as e:
                return None

    @staticmethod
    def write_json(filepath,data):
        with open(filepath,'w') as f:
            json.dump(data,f,ensure_ascii=False)

    @staticmethod
    def delete(path):
        """删除文件/文件夹
        """
        if os.path.isfile(path):
           try:
               os.remove(path)
           except Exception as e:
               return False,str(e)
        elif os.path.isdir(path):
            try:
                shutil.rmtree(path)
            except Exception as e:
                return False,str(e)
        return True,''

    @staticmethod
    def delete_bulk(files):
        """删除多个文件/文件夹
        """
        msg = ''
        flag = True
        for file in files:
            _flag,_msg = FileHelper.delete(file)
            flag = _flag and flag
            if _msg != '':
                msg = msg + ',' + _msg
        return flag,msg


    @staticmethod
    def copy(source_file,save_dir):
        """复制文件/文件夹
        """
        try:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            basename = os.path.basename(source_file)
            if os.path.isfile(source_file):
                file_name = os.path.splitext(basename)[0]
                file_ext = os.path.splitext(basename)[1]
                save_filepath = os.path.join(save_dir,basename)
                if os.path.exists(save_filepath):
                    save_filepath = os.path.join(save_dir,file_name + '_' + StringHelper.get_random_num() + file_ext)
                shutil.copy(source_file,save_filepath)
            elif os.path.isdir(source_file):
                save_dir_path = os.path.join(save_dir,basename)
                if os.path.exists(save_dir_path):
                    save_dir_path = os.path.join(save_dir,basename + '_' + StringHelper.get_random_num())
                shutil.copytree(source_file,save_dir_path)
            else:
                return False,source_file + ' 不是目录也不是文件'

            return True,''
        except Exception as e:
            return False,str(e)

    @staticmethod
    def copy_bulk(files,save_dir):
        """复制多个文件/文件夹
        """
        msg = ''
        flag = True
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        for file in files:
            _flag,_msg = FileHelper.copy(file,save_dir)
            flag = _flag and flag
            if _msg != '':
                msg = msg + ',' + _msg
        return flag,msg

    @staticmethod
    def move(source_file,save_dir):
        """移动文件/文件夹
        """
        try:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            basename = os.path.basename(source_file)
            if os.path.isfile(source_file):
                file_name = os.path.splitext(basename)[0]
                file_ext = os.path.splitext(basename)[1]
                save_filepath = os.path.join(save_dir,basename)
                if os.path.exists(save_filepath):
                    save_filepath = os.path.join(save_dir,file_name + '_' + StringHelper.get_random_num() + file_ext)
                shutil.move(source_file,save_filepath)
            elif os.path.isdir(source_file):
                save_dir_path = os.path.join(save_dir,basename)
                if os.path.exists(save_dir_path):
                    save_dir_path = os.path.join(save_dir,basename + '_' + StringHelper.get_random_num())
                shutil.move(source_file,save_dir_path)
            else:
                return False,source_file + ' 不是目录也不是文件'
            return True,''
        except Exception as e:
            return False,str(e)


    @staticmethod
    def move_bulk(files,save_dir):
        """移动多个文件/文件夹
        """
        msg = ''
        flag = True
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        for file in files:
            _flag,_msg = FileHelper.move(file,save_dir)
            flag = _flag and flag
            if _msg != '':
                msg = msg + ',' + _msg
        return flag,msg

    @staticmethod
    def rename(filepath,new_name):
        """重命名
        filepath : 文件/目录名
        new_name : 新文件/目录名
        """
        os.rename(filepath,os.path.join(os.path.dirname(filepath),new_name))


    @staticmethod
    def tar(filepath,tartype='tar',save_dir='',save_file_name='', mode='w'):
        """创建tar文件
        tartype tar或gztar 默认值 tar
        save_dir 保存目录 默认为当前目录
        save_file_name 压缩包文件名 不包含后缀
        "mode 'w'为写 'a'为追加 默认'w'
        返回 flag,msg   flag:操作是否成功 msg成功则为存档文件路径，失败则为错误信息
        """
        try:
            if tartype not in 'tar,gztar':
                return False,'错误的存档类型，应该为tar或者gztar'
            basename = os.path.basename(filepath)
            parent_dir = os.path.dirname(filepath)
            file_name = os.path.splitext(basename)[0]
            if save_dir != '':
                parent_dir = save_dir
            if save_file_name != '':
                file_name = save_file_name
            tar_ext = '.tar' if tartype == 'tar' else '.tar.gz'
            save_path = os.path.join(parent_dir,file_name + tar_ext)
            if os.path.isfile(filepath):
                if tartype == 'tar':
                    tar = tarfile.open(save_path,mode)
                else:
                    tar = tarfile.open(save_path,mode + ':gz')
                tar.add(filepath,basename)
                tar.close()
            elif os.path.isdir(filepath):
                if tartype == 'tar':
                    tar = tarfile.open(save_path,mode)
                else:
                    tar = tarfile.open(save_path,mode + ':gz')
                for root,dir,files in os.walk(filepath):
                    for file in files:
                        fullpath = os.path.join(root,file)
                        tar.add(fullpath,fullpath[len(os.path.dirname(filepath)):]) #为了在压缩包内保存文件目录结构
                tar.close()
            else:
                 return False,filepath + ' 不是目录也不是文件'
            return True,save_path
        except Exception as e :
            return False,str(e)

    @staticmethod
    def untar(filepath,save_dir=''):
        """提取tar文件
        "save_dir 保存目录 默认为当前目录
        返回 flag,msg   flag:操作是否成功 msg成功则为提取路径，失败则为错误信息
        """
        try:

            basename = os.path.basename(filepath)
            parent_dir = os.path.dirname(filepath)
            file_name = os.path.splitext(basename)[0]
            file_ext = os.path.splitext(basename)[1]
            if file_ext == '.tar':
                tar = tarfile.open(filepath, 'r')
            elif file_ext == '.gz' and file_name.split('.')[-1] == 'tar':
                tar = tarfile.open(filepath, 'r:gz')
                _filename = file_name.split('.')
                _filename.pop()
                file_name = ''.join(_filename)
            else:
                return False,'错误的文件类型，必须为tar或tar.gz'
            if save_dir != '':
                parent_dir = save_dir
            extract_dir = os.path.join(parent_dir,file_name)
            tar.extractall(extract_dir)
            tar.close()
            return True,extract_dir
        except Exception as e:
            return False,str(e)


    @staticmethod
    def zip(filepath,save_dir='',save_file_name='',mode='w'):
        """创建zip压缩文件
        save_dir 保存目录 默认为当前目录
        save_file_name 压缩包文件名 不包含后缀
        pwd 密码
        "mode 'w'为写 'a'为追加 默认'w'
        返回 flag,msg   flag:操作是否成功 msg成功则为存档文件路径，失败则为错误信息
        """
        try:
            basename = os.path.basename(filepath)
            parent_dir = os.path.dirname(filepath)
            file_name = os.path.splitext(basename)[0]
            if save_dir != '':
                parent_dir = save_dir
            if save_file_name != '':
                file_name = save_file_name
            save_zip_path = os.path.join(parent_dir,file_name + '.zip')
            if os.path.isfile(filepath):
                with zipfile.ZipFile(save_zip_path, mode) as zip:
                    zip.write(filepath,basename)
            elif os.path.isdir(filepath):
                with zipfile.ZipFile(save_zip_path, mode) as zip:
                    for root,dir,files in os.walk(filepath):
                        for file in files:
                            fullpath = os.path.join(root,file)
                            zip.write(fullpath,fullpath[len(os.path.dirname(filepath)):])
                            #为了在压缩包内保存文件目录结构
            else:
                 return False,filepath + ' 不是目录也不是文件'
            return True,save_zip_path
        except Exception as e :
            return False,str(e)

    @staticmethod
    def unzip(filepath,save_dir=''):
        """解压zip压缩文件
        "save_dir 保存目录 默认为当前目录
        返回 flag,msg   flag:操作是否成功 msg成功则为解压路径，失败则为错误信息
        """
        try:
            zip = zipfile.ZipFile(filepath)
            basename = os.path.basename(filepath)
            parent_dir = os.path.dirname(filepath)
            file_name = os.path.splitext(basename)[0]
            if save_dir != '':
                parent_dir = save_dir
            extract_dir = os.path.join(parent_dir,file_name)
            zip.extractall(extract_dir)
            return True,extract_dir
        except Exception as e:
            return False,str(e)

    @staticmethod
    def compress(type,filepath,save_dir='',save_file_name='',pwd=None,ignore_dir=None,ignore_ext=None,ignore_file=None,part=None):
        basename = os.path.basename(filepath)
        file_name = os.path.splitext(basename)[0]
        parent_dir = os.path.dirname(filepath)
        if save_file_name != '':
                file_name = save_file_name
        if save_dir != '':
             parent_dir = save_dir
        save_file_path = os.path.join(parent_dir,file_name) + '.' + type
        sysstr = platform.system()
        ignore_cmd = ''
        part_cmd = ''
        if ignore_dir:
            for d in ignore_dir:
                if d:
                    ignore_cmd+=' -xr!' + d
        if ignore_file:
            for f in ignore_file:
                if f:
                    ignore_cmd+=' -xr!' + f
        if ignore_ext:
            for e in ignore_ext:
                if e:
                    ignore_cmd+=' -xr!*.' + e
        if part:
            part_cmd = '-v' + part
        if sysstr == "Windows":
            pwdcmd = '-p' + pwd if pwd  else ''
            cmd = WINDOWS_7ZIP_PATH + ' a -t{0} {1} {2} {3}'.format(type,pwdcmd + ' ' + ignore_cmd + ' ' + part_cmd,save_file_path,filepath)
        elif sysstr == "Linux":
            pwdcmd = '-p' + pwd if pwd  else ''
            cmd = '7za a -t{0} {1} {2} {3}'.format(type,pwdcmd + ' ' + ignore_cmd + ' ' + part_cmd,save_file_path,filepath)
        else:
            return False,sysstr + '是啥系统?'
        status,result = subprocess.getstatusoutput(cmd)
        flag = (status == 0)
        return flag,save_file_path if flag else result

    @staticmethod
    def create_archive(filepath,archive_type,save_file_name='',mode='w',save_dir='',pwd=None):
        """创建文件/文件夹存档
        archive_type有效值 zip tar gztar
        save_file_name 压缩包文件名 不包含后缀
        mode 'w'为写 'a'为追加 默认'w'
        返回 flag,msg   flag:操作是否成功 msg成功则为存档文件路径，失败则为错误信息
        """
        try:
            if not os.path.exists(filepath):
                return False,'文件不存在'
            parent_dir = os.path.dirname(filepath)
            dir_name = os.path.basename(filepath)
            save_path = os.path.join(parent_dir,dir_name)
            if archive_type == 'zip':
                return FileHelper.zip_7z(filepath,save_file_name=save_file_name,save_dir=save_dir,pwd=pwd)
            elif archive_type == 'tar':
                return FileHelper.tar(filepath,save_file_name=save_file_name,mode=mode,save_dir=save_dir)
            elif archive_type == 'gztar':
                return FileHelper.tar(filepath,'gztar',save_file_name=save_file_name,mode=mode,save_dir=save_dir)
            else:
                return False,'存档类型错误'
        except Exception as e:
            return False,str(e)

    @staticmethod
    def create_archive_bulk(files,archive_type):
        """创建多个存档
        返回 flag,msg   flag:操作是否成功 msg成功则为存档文件路径，失败则为错误信息
        """
        msg = ''
        flag = True
        save_file_name = StringHelper.get_random_num() + '多个文件'
        is_gztar = False
        if archive_type == 'gztar': #gztar无法设置为追加 所以先打包为tar然后在打包为gztar
            is_gztar = True
            archive_type = 'tar'
        for file in files:
            _flag,_msg = FileHelper.create_archive(file,archive_type,save_file_name=save_file_name,mode='a') #设置为追加
            flag = _flag and flag
            if _msg != '':
                if msg == '':
                    msg = _msg
                else:
                    msg = msg + ',' + _msg
        if is_gztar:
            tarfilepath = msg.split(',')[0]
            _flag,_msg = FileHelper.create_archive(tarfilepath,'gztar')
            FileHelper.delete(tarfilepath)
            flag = _flag and flag
            msg = msg + ',' + _msg
        return flag,msg

    @staticmethod
    def extract_archive(filepath,extract_type):
        """提取存档
        extract_type有效值:current(当前位置) folder(当前位置的文件夹) location(指定位置)
        返回 flag,msg   flag:操作是否成功 msg成功则为提取路径，失败则为错误信息
        """
        try:
            basename = os.path.basename(filepath)
            file_name = os.path.splitext(basename)[0]
            file_ext = os.path.splitext(basename)[1]
            file_dir = os.path.dirname(filepath)
            if file_ext not in '.zip.tar.gz':
                return False,'存档类型错误,必须为(.zip,.tar,.tar.gz)'
            if file_ext == '.gz':
                if not (file_name.split('.')[-1] == 'tar'):
                    return False,'存档类型错误,必须为(.zip,.tar,.tar.gz)'
            if extract_type == 'current':
                if file_ext == '.zip':
                    return FileHelper.unzip(filepath)
                if file_ext == '.tar' or (file_ext == '.gz' and file_name.split('.')[-1] == 'tar'):
                    return FileHelper.untar(filepath)
            elif extract_type == 'folder':
                save_dir = os.path.join(file_dir,file_name)
                if file_ext == '.zip':
                    return FileHelper.unzip(filepath,save_dir)
                if file_ext == '.tar' or (file_ext == '.gz' and file_name.split('.')[-1] == 'tar'):
                    return FileHelper.untar(filepath,save_dir)
            elif extract_type == 'location':
                #解压到指定位置.......
                pass
            else:
                return False,'提取存档类型错误'
            return True,''
        except Exception as e:
            return False,str(e)


    @staticmethod
    def extract_archive_bulk(files,extract_type):
        """提取多个存档
        返回 flag,msg   flag:操作是否成功 msg成功则为提取路径，失败则为错误信息
        """
        msg = ''
        flag = True
        for file in files:
            _flag,_msg = FileHelper.extract_archive(file,extract_type)
            flag = _flag and flag
            if _msg != '':
                msg = msg + ',' + _msg
        return flag,msg

    @staticmethod
    def get_info(filepath):
        """获取文件/文件夹夹信息
        return {'filetype':filetype,'filename':filename,'file_ext':file_ext,'filepath':filepath, 'size':size, 'permission':permission,'file_count':file_count,
                'access_time':access_time, 'create_time':create_time, 'modify_time':modify_time}
        filetype:file or folder
        """
        size = 0.00
        #文件数
        file_count = 0
        basename = os.path.basename(filepath)
        filename = os.path.splitext(basename)[0]
        file_ext = ''
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath) / 1024 / 1024
            if size > 1024:
                size = round(size / 1024,2)
                size = str(size) + 'GB'
            else:
                size = round(size,2)
                size = str(size) + 'MB'
            file_count = 1
            filetype = 'file'
            file_ext = os.path.splitext(basename)[1]
        elif os.path.isdir(filepath):
            for root, dirs, files in os.walk(filepath):
                size += sum([os.path.getsize(os.path.join(root, file)) for file in files])
                file_count += len(files)
            size = size / 1024 / 1024
            if size > 1024:
                size = round(size / 1024,2)
                size = str(size) + 'GB'
            else:
                size = round(size,2)
                size = str(size) + 'MB'
            filetype = 'folder'
        #文件的访问时间
        access_time = os.path.getatime(filepath)
        access_time = FileHelper.timestamp_to_date(access_time)
        #文件的创建时间
        create_time = os.path.getctime(filepath)
        create_time = FileHelper.timestamp_to_date(create_time)
        #文件的修改时间
        modify_time = os.path.getmtime(filepath)
        modify_time = FileHelper.timestamp_to_date(modify_time)
        permission = FileHelper.get_permission(filepath)
        return {'filetype':filetype,'filename':filename,'filepath':filepath, 'size':size, 'permission':permission,'file_count':file_count,
                'access_time':access_time, 'create_time':create_time, 'modify_time':modify_time}

    @staticmethod
    def get_permission(filepath):
        """获取文件/文件夹权限
        返回值 例如： 可读,可写,不可执行
        """
        readable = '可读' if os.access(filepath,os.R_OK) else '不可读'
        writable = '可写' if os.access(filepath,os.W_OK) else '不可写'
        executable = '可执行' if os.access(filepath,os.X_OK) else '不可执行'
        return readable + ',' + writable + ',' + executable


    @staticmethod
    def timestamp_to_date(timestamp):
        """将时间戳转换为格式化日期字符串
        """
        _time = time.localtime(timestamp)
        return time.strftime('%Y-%m-%d %H:%M:%S',_time)

if __name__ == '__main__':
    #files = [r'D:\Save\temp\bbb',r'D:\Save\temp\11.zip']
    #print(FileHelper.create_archive_bulk(files,'tar'))
    #FileHelper.untar(r'D:\Save\temp\11_9595199\11.tar.gz',r'D:\Save\temp\bbb')
    #print(FileHelper.compress('zip','D:\\Save\\temp\\MyApplication','D:\\Save\\backuptemp','testsite','123',".idea","properties","MyApplication.iml"))
    
    pass
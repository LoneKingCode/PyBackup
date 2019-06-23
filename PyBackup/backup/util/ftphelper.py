encoding ='utf-8'
from ftplib import FTP
import time
import zipfile
import os

class FtpHelper:
    def __init__(self, host ,username,password,port = 21,pasv=0):
        self.ftp = FTP()
        # self.ftp.set_debuglevel(2) #打开调试级别2，显示详细信息
        self.ftp.set_pasv(pasv) #0主动模式 1 #被动模式
        self._isdir = False
        self.path = ""
        self.ftp.encoding = 'utf-8'
        self.ftp.connect(host, port)
        self.ftp.login(username, password)
        #self.ftp.putcmd('opts utf8 off')


    def download_file(self, local_file, remote_file):#下载单个文件
        file_handler = open(local_file, 'wb')
        #print(file_handler)
        self.ftp.retrbinary("RETR %s" % (remote_file), file_handler.write)#接收服务器上文件并写入本地文件
        file_handler.close()
        return True

    def upload_file(self, local_file, remote_file):
        if os.path.isfile(local_file) == False:
            return False
        file_handler = open(local_file, "rb")
        self.ftp.storbinary('STOR %s' % remote_file, file_handler, 4096)#上传文件
        file_handler.close()
        return True

    def upload_dir(self, local_dir, remote_dir):
        if os.path.isdir(local_dir) == False:
            return False
        #print("local_dir:" + local_dir)
        local_names = os.listdir(local_dir)
        #print(local_names)
        #print(remote_dir)
        self.ftp.cwd(remote_dir)
        for local in local_names:
            src = os.path.join(local_dir, local)
            if os.path.isdir(src):
                self.upload_dir(src, local)
            else:
                self.upload_file(src, local)

        self.ftp.cwd("..")
        return

    def download_dir(self, local_dir, remote_dir):#下载整个目录下的文件
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        self.ftp.cwd(remote_dir)
        remote_names = self.ftp.nlst()
        #print(remote_names)
        #print(self.ftp.nlst("/del1"))
        for file in remote_names:
            local = os.path.join(local_dir, file)
            if self.is_dir(file):
                self.download_dir(local, file)
            else:
                self.download_file(local, file)
        self.ftp.cwd("..")
        return

    def show(self, list):
        result = list.lower().split(" ")
        if self.path in result and result[0].startswith('d'):
            self._isdir = True

    def is_dir(self, path):
        self._isdir = False
        self.path = path
        # this use callback function ,that will change isdir value
        self.ftp.retrlines('LIST', self.show)
        return self._isdir

    def get_files(self,path):
        self.ftp.cwd(path)
        return self.ftp.nlst()

    def delete_file(self,path,filename):
        self.ftp.cwd(path)
        self.ftp.delete(filename)

    def quit(self):
        self.ftp.quit()

if __name__ == "__main__":
    ftp = FtpHelper('.11.cn','11@', '111')

    ftp.download_dir('D:\\Save\\temp\\2\\WEB', '/WEB') # 从目标目录下载到本地目录E盘

    ftp.quit()

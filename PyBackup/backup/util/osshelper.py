import os
from oss2 import SizedFileAdapter, determine_part_size
from oss2.models import PartInfo
import oss2
from util.loghelper import LogHelper

class OssHelper:

    def __init__(self,keyid,keysecret,url,bucket):
        self.auth = oss2.Auth(keyid, keysecret)
        self.bucket = oss2.Bucket(self.auth, url, bucket)

    def get_file_list(self,dir = ''):
        return [b.key for b in oss2.ObjectIterator(self.bucket,prefix=dir)]

    def upload(self,upload_path,filepath):
        """
        upload_path 文件上传后的完整路径包括本身
        filepath 本地文件路径
        """
        key = upload_path
        filename = filepath

        total_size = os.path.getsize(filename)
        # determine_part_size方法用来确定分片大小。
        part_size = determine_part_size(total_size, preferred_size=100 * 1024)

        # 初始化分片。
        upload_id = self.bucket.init_multipart_upload(key).upload_id
        parts = []

        # 逐个上传分片。
        with open(filename, 'rb') as fileobj:
            part_number = 1
            offset = 0
            while offset < total_size:
                num_to_upload = min(part_size, total_size - offset)
		        # SizedFileAdapter(fileobj, size)方法会生成一个新的文件对象，重新计算起始追加位置。
                result = self.bucket.upload_part(key, upload_id, part_number,
                                            SizedFileAdapter(fileobj, num_to_upload))
                parts.append(PartInfo(part_number, result.etag))

                offset += num_to_upload
                part_number += 1

        # 完成分片上传。
        self.bucket.complete_multipart_upload(key, upload_id, parts)

        # 验证分片上传。
        with open(filename, 'rb') as fileobj:
            if not self.bucket.get_object(key).read() == fileobj.read():
                msg='上传' + filename + '出错，验证分片失败'
                print(msg)
                LogHelper.info(msg)


    def delete(self,obj_name):
        self.bucket.delete_object(obj_name)

if __name__ == '__main__':
    oss = OssHelper('44','55','oss-cn-66.66.com','66')
    print(oss.get_file_list('sites/'))

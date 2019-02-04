import os
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys

class CosHelper:
    def __init__(self,keyid,keysecret,region,bucket):
        secret_id = keyid      # 替换为用户的 secretId
        secret_key = keysecret      # 替换为用户的 secretKey
        region = region     # 替换为用户的 Region
        token = None                # 使用临时密钥需要传入 Token，默认为空，可不填
        scheme = 'https'            # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
        self.bucket = bucket
        self.client = CosS3Client(config)

    def get_file_list(self,dir = ''):
        response = self.client.list_objects(Bucket=self.bucket,
            Prefix=dir,
            Delimiter='/',
            EncodingType='url')
        if 'Contents' in response.keys():
            return [b['Key'] for b in response['Contents']]
        else:
            return []

    def upload(self,upload_path,filepath):
        """
        upload_path 文件上传后的完整路径包括本身
        filepath 本地文件路径
        """
        response = self.client.upload_file(Bucket=self.bucket,
            LocalFilePath=filepath,
            Key=upload_path,
            PartSize=10,
            MAXThread=10,
            EnableMD5=False)

    def delete(self,obj_name):
        response = self.client.delete_object(Bucket=self.bucket,
            Key=obj_name)

if __name__ == '__main__':
    cos = CosHelper('11','22','ap-33','backup-44')
    print(cos.get_file_list('sites'))

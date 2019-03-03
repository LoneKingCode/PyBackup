import requests
import json
from config import *
import time
import os
from urllib import parse
from util.filehelper import FileHelper

reply_url = 'https://onedrive.live.com/about/business/'
redirect_uri = 'http://localhost/onedrive-login'
auth_url = 'https://login.microsoftonline.com/common/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=offline_access%20files.readwrite.all'
api_auth_url = "https://login.microsoftonline.com/common/oauth2/token"
api_discovery_url = "https://api.office.com/discovery/v2.0/me/services"
api_discovery_id = "https://api.office.com/discovery/"
app_url = 'https://graph.microsoft.com/'
refresh_param = 'client_id={client_id}&redirect_uri={redirect_uri}&client_secret={client_secret}&refresh_token={refresh_token}&grant_type=refresh_token&resource={resource}'



def init_multi_auth():
    for option in ONE_DRIVE_OPTION:
        print('开始认证' + option['name'])
        od = OneDriveHelper(option['name'])
        od.auth()

class OneDriveHelper(object):
    def __init__(self,name):
        self.name = name
        self.token_file_name = name + '_onedrive_token.json'
        self.token_filepath = os.path.join(str(ROOT_DIR),'data',self.token_file_name)
        self.client_id = ONE_DRIVE_CLIENT['client_id']
        self.client_secret = ONE_DRIVE_CLIENT['client_secret']

    def auth(self):
        print(auth_url.format(client_id=self.client_id,redirect_uri=redirect_uri))
        print('请用浏览器打开上面链接，登陆等待跳转后，复制URL地址中code参数的值，注意不要多复制后面的&session_state参数')
        code = input('请输入code:')
        auth_param = 'client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={redirect_uri}&resource=https://api.office.com/discovery/'
        auth_param = auth_param.format(client_id=self.client_id,code=code,client_secret=self.client_secret,redirect_uri=redirect_uri)
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(api_auth_url, data=auth_param, headers=headers)
        data = json.loads(response.text)

        access_token = data['access_token']

        discovery_token = self.refresh_token(data.get('refresh_token'),api_discovery_id)
        url,urlid = self.get_onedrive_api_urls(discovery_token.get('access_token'))
        token = self.refresh_token(discovery_token.get('refresh_token'),urlid)

        if os.path.exists(self.token_filepath):
            data = FileHelper.open_json(self.token_filepath)
            try:
                data[self.name] = token
                data[self.name]['api_url'] = url
                data[self.name]['api_url_id'] = urlid
            except:
                token['api_url'] = url
                token['api_url_id'] = urlid
                data = {self.name:token}
        else:
            token['api_url'] = url
            token['api_url_id'] = urlid
            data = {self.name:token}

        FileHelper.write_json(self.token_filepath,data)
        #print(data[self.name])
        print('保存token完成')

    def refresh_token(self,refresh_token,resource):
        auth_param = refresh_param.format(client_id=self.client_id,redirect_uri=redirect_uri,client_secret=self.client_secret,refresh_token=refresh_token,resource=resource)
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(api_auth_url, data=auth_param, headers=headers)
        data = json.loads(response.text)
        return data

    def get_token(self):
        if os.path.exists(self.token_filepath):
            token = FileHelper.open_json(self.token_filepath).get(self.name)
            if time.time() > float(token.get('expires_on')):
                print('token已过期 重新获取')
                refresh_token = token.get('refresh_token')
                discovery_token = self.refresh_token(refresh_token,api_discovery_id)
                url,urlid = self.get_onedrive_api_urls(discovery_token.get('access_token'))
                token = self.refresh_token(discovery_token.get('refresh_token'),urlid)
                if token.get('access_token'):
                    data = FileHelper.open_json(self.token_filepath)
                    data[self.name] = token
                    data[self.name]['api_url'] = url
                    data[self.name]['api_url_id'] = urlid
                    FileHelper.write_json(self.token_filepath,data)
                    return token.get('access_token')
                else:
                    print('获取失败,没有access_token:')
                    print(token)
            else:
                return token.get('access_token')
    #获取配置文件中保存的api_url
    def get_api_url(self):
        return FileHelper.open_json(self.token_filepath).get(self.name).get('api_url')

    def upload(self,remote_path,filepath):
        access_token = self.get_token()
        headers = {'Authorization':'Bearer {}'.format(access_token),'Content-Type':'text/plain','Accept':'application/json; odata.metadata=none'}
        url = self.get_api_url() + '/drive/root:/{}:/content'.format(parse.quote(remote_path.encode('utf-8')))
        r = requests.put(url,headers=headers,data=open(filepath,'rb'))
        try:
            data = json.loads(r.text)
            if data.get('error'):
                print(url)
                print(data.get('error').get('message'))
            elif r.status_code == 201 or r.status_code == 200:
                print('上传 {} 成功,保存位置{}'.format(filepath,remote_path))
            else:
                print('上传失败')
                print(data)
        except Exception as e:
            print('上传失败')
            print(str(e))

    def delete(self,filepath):
        access_token = self.get_token()
        headers = {'Authorization':'Bearer {}'.format(access_token),'Content-Type':'text/plain','Accept':'application/json; odata.metadata=none'}
        r = requests.delete(self.get_api_url() + '/drive/root:/{0}'.format(filepath),headers=headers)
        return r.status_code == 204

    def get_file_list(self,dir):
        dir = dir.lstrip('/')
        access_token = self.get_token()
        headers = {'Authorization':'Bearer {}'.format(access_token),'Content-Type':'text/plain','Accept':'application/json; odata.metadata=none'}
        r = requests.get(self.get_api_url() + '/drive/root:/{0}?expand=children(select=lastModifiedDateTime,size,name,folder,file)'.format(dir),headers=headers)
        try:
            return json.loads(r.text).get('children')
        except :
            return[]

    def get_onedrive_api_urls(self,access_token):
        headers = {'Authorization':'Bearer {}'.format(access_token)}
        response = requests.get(api_discovery_url, headers=headers)
        data = json.loads(response.text)
        # [0] 是 1.0的 [1]是2.0的
        return data['value'][1]['serviceEndpointUri'],data['value'][1]['serviceResourceId']

if __name__ == '__main__':
    #init_multi_auth()
    a = OneDriveHelper('backup1')
    a.get_file_list()



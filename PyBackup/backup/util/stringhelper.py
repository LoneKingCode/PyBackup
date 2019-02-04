import time
import random
import math
import urllib.parse
class StringHelper(object):
    @staticmethod
    def get_random_num(length=7):
        return str(random.random() * math.pow(10,length)).split('.')[0]
    @staticmethod
    def get_random_str(length=7):
        items = (','.join('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789')).split(',')
        return str(''.join(random.sample(items, length)))
    @staticmethod
    def urlencode(s):
        return urllib.parse.quote(s)
    @staticmethod
    def urldecode(s):
       return urllib.parse.unquote(s)

if __name__ == '__main__':
    print(StringHelper.urlencode('http://www.baidu.com/啊'))

# coding:utf-8
import os
import logging
from logging import handlers

class LogHelper(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__)) #项目路径
    rootPath = os.path.split(BASE_DIR)[0]
    path = os.path.join(rootPath,'log')
    os.makedirs(path)
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'critical':logging.CRITICAL
    }#日志级别关系映射
    @staticmethod
    def debug(msg):
        LogHelper.log(msg,'debug')
    @staticmethod
    def info(msg):
        LogHelper.log(msg,'info')
    @staticmethod
    def warning(msg):
        LogHelper.log(msg,'warning')
    @staticmethod
    def error(msg):
        LogHelper.log(msg,'error')
    @staticmethod
    def critical(msg):
        LogHelper.log(msg,'critical')
    @staticmethod
    def log(msg,level = 'info'):
        filepath = os.path.join(LogHelper.path,level + '.log')
        logger = logging.getLogger(filepath)
        streamhandler = handlers.TimedRotatingFileHandler(filename=filepath,when='D',backupCount=3,encoding='utf-8')
        streamhandler.setLevel(LogHelper.level_relations[level])
        formatter = logging.Formatter('%(asctime)s - %(levelname)s   - %(message)s')
        streamhandler.setFormatter(formatter)

        logger.addHandler(streamhandler)
        logger.error(msg)

        #  添加下面一句，在记录日志之后移除句柄
        logger.removeHandler(streamhandler)

if __name__ == '__main__':
    LogHelper.warning('info1')
    LogHelper.warning('info2')
    LogHelper.warning('info3')



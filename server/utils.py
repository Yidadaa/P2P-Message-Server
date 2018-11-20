"""
工具函数
"""

import time, hashlib

def get_path_of(filename):
  file_path = __file__
  rindex = len(file_path)
  seperator = '/'
  try:
    rindex = file_path.rindex('/')
  except ValueError:
    rindex = file_path.rindex('\\')
    seperator = '\\'
  return file_path[0:rindex]  + seperator + filename

def hash_file_name(filename:str):
  """
  返回hash后的文件名字
  """
  salt = str(time.time_ns())
  extension = filename.rsplit('.', 1)[1]
  string = filename + salt
  return hashlib.md5(string.encode('utf-8')).hexdigest() + '.' + extension
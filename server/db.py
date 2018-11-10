import sqlite3
import os

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

class DB:
  def __init__(self):
    path = get_path_of('p2pmessage.db')
    print(path)
    self.conn = sqlite3.connect(path, check_same_thread=False)
    print('Connected to Database')

  def add_user(self, user:dict):
    """
    新增用户到表中
    """
    cursor = self.conn.cursor()
    keys = list(user.keys())
    values = [str(i) if type(i) is not str else "'%s'" % i for i in list(user.values())]
    userid = None
    try:
      sql = 'INSERT INTO USER (%s) VALUES (%s)' % (','.join(keys), ','.join(values))
      cursor.execute(sql)
      userid = cursor.execute('SELECT max(id) FROM USER')
      self.conn.commit()
      userid = list(userid)
      userid = userid[0][0] if len(userid) > 0 else -1
    except Exception as e:
      return False, e
    return True, userid

import sqlite3
import os, time

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

def array2dict(keys, values):
  """
  将扁平化的数组转化为字典
  """
  dicts = {}
  for i in range(len(keys)):
    if type(keys[i]) is dict:
      for k in keys[i].keys():
        dicts[k] = array2dict(keys[i][k], values[i: i + len(keys[i][k])])
    else:
      dicts[keys[i]] = values[i]
  return dicts

class DB:
  def __init__(self):
    path = get_path_of('p2pmessage.db')
    print(path)
    self.conn = sqlite3.connect(path, check_same_thread=False)
    print('Connected to Database')

  def update_user_status(self, userid:int)->str:
    """
    更新用户的上次在线时间以及用户状态
    """
    now = int(time.time() * 1000)
    sql = 'UPDATE USER SET last_online = %d, status = 1 WHERE id = %d' % (now, int(userid))

    self.conn.execute(sql)
    self.conn.commit()

  def add_user(self, user:dict):
    """
    新增用户到表中
    """
    cursor = self.conn.cursor()
    keys = list(user.keys())
    values = [str(i) if type(i) is not str else "'%s'" % i for i in list(user.values())]

    userid = None

    keys.append('last_online')
    values.append(int(time.time() * 1000))
    keys.append('status')
    values.append(1)

    try:
      sql = 'INSERT INTO USER (%s) VALUES (%s)' % (','.join(keys), ','.join(values))
      cursor.execute(sql)
      userid = cursor.execute('SELECT max(id) FROM USER').fetchone()
      self.conn.commit()
      userid = userid[0] if len(userid) > 0 else -1
    except Exception as e:
      return False, str(e)
    return True, userid

  def check_user(self, user:dict)->(bool, dict):
    """
    检查用户登录
    """
    cursor = self.conn.cursor()
    if 'name' not in user or 'password' not in user:
      return False, '缺少必要的参数'
    sql = 'SELECT * FROM USER  WHERE name = "%s" AND password = "%s"'%(user['name'], user['password'])

    keys = ['id', 'name', 'address', 'avatar', 'email', 'password', 'last_online', 'status']

    try:
      res = cursor.execute(sql)
      self.conn.commit()
      res = list(res)
      _user = {}
      if len(res) > 0:
        _user = array2dict(keys, res[0])
        self.update_user_status(_user['id'])
      else:
        raise(Exception('No Such User'))
      res = _user
    except Exception as e:
      return False, str(e)
    return True, res

  def collect_messages(self, userid:int)->(bool, list):
    # 获取用户的消息
    cursor = self.conn.cursor()
    sql = 'SELECT m.id, m.status, m.content, m.ts, u.id, u.name, u.avatar, u.address, u.email, u.last_online, u.status \
      FROM MESSAGE AS m INNER JOIN USER as u \
      ON m.to_userid = %d OR m.from_userid = %d WHERE m.from_userid = u.id' % (int(userid), int(userid))

    keys = ['id', 'status', 'content', 'ts', { 'user': ['id', 'name', 'avatar', 'address', 'email', 'last_online', 'status'] }]

    try:
      res = cursor.execute(sql)
      self.conn.commit()
      self.update_user_status(userid)
      res = list(res)
      messages = [array2dict(keys, v) for v in res]

    except Exception as e:
      return False, str(e)
    return True, messages

  def collect_contacts(self, userid:int)->(bool, list):
    # 获取用户的联系人
    cursor = self.conn.cursor()
    sql = 'SELECT c.id, c.name, c.avatar, c.address, c.email, c.last_online, c.status \
      FROM CONTACTS AS u INNER JOIN USER as c \
      ON u.id = %d WHERE c.id = u.contact_id' % (int(userid))

    print(sql)

    keys = ['id', 'name', 'avatar', 'address', 'email', 'last_online', 'status']

    try:
      res = cursor.execute(sql)
      self.conn.commit()
      self.update_user_status(userid)
      res = list(res)
      contacts = [array2dict(keys, v) for v in res]
    except Exception as e:
      return False, str(e)

    return True, contacts

  def add_message(self, from_userid:int, to_userid:int, content:str, ts:int)->(bool, str):
    cursor = self.conn.cursor()

    sql = 'INSERT INTO MESSAGE (from_userid, to_userid, content, ts)\
      VALUES (%d, %d, "%s", %d)' % (int(from_userid), int(to_userid), content, int(ts))

    print(sql)
    msgid = -1

    try:
      cursor.execute(sql)
      msgid = cursor.execute('SELECT max(id) FROM MESSAGE').fetchone()
      self.conn.commit()
      self.update_user_status(from_userid)
      msgid = msgid[0]
    except Exception as e:
      return False, str(e)
    return True, msgid
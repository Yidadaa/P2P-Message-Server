import sqlite3
import os, time
from utils import get_path_of

USER_KEYS = ['id', 'name', 'address', 'avatar', 'email', 'password', 'last_online', 'status']
COULD_CHANGE_KEYS = ['name', 'address', 'avatar', 'email', 'last_online', 'status']

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
      userid = cursor.lastrowid
      self.conn.commit()
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

    keys = USER_KEYS

    print(sql)

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
    sql = 'SELECT * FROM MESSAGE as m WHERE m.to_userid = %d OR m.from_userid = %d' % (int(userid), int(userid))

    try:
      messages = cursor.execute(sql).fetchall()
      self.conn.commit()
      self.update_user_status(userid)

    except Exception as e:
      return False, str(e)
    return True, messages

  def collect_contacts(self, userid:int)->(bool, list):
    # 获取用户的联系人
    cursor = self.conn.cursor()

    keys = ['id', 'name', 'avatar', 'address', 'email', 'last_online', 'status']

    sql = 'SELECT %s \
      FROM CONTACTS AS u INNER JOIN USER as c \
      ON u.id = %d WHERE c.id = u.contact_id' % (','.join(['c.' + k for k in keys]), int(userid))

    print(sql)

    try:
      contacts = cursor.execute(sql).fetchall()
      self.conn.commit()
      self.update_user_status(userid)
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
      msgid = cursor.lastrowid
      self.conn.commit()
      self.update_user_status(from_userid)
    except Exception as e:
      return False, str(e)
    return True, msgid

  def update_user_info(self, user_info:dict, userid:int):
    """
    更新用户信息
    """
    filtered_keys = map(lambda k: '='.join([k, '"' + user_info[k] + '"']), user_info.keys())

    cursor = self.conn.cursor()

    sql = 'UPDATE USER SET %s WHERE id = %d'\
      % (','.join(filtered_keys), userid)

    print(sql)

    try:
      cursor.execute(sql)
      self.conn.commit()
      self.update_user_status(userid)
    except Exception as e:
      return False, str(e)
    return True, ''

  def start_connection(self, from_uid, from_ip, from_port, to_uid):
    """
    更新连接状态
    """
    cursor = self.conn.cursor()

    sql = '''INSERT INTO CONNNECIONS (from_uid, from_ip, from_port, to_uid, status)
      VALUES (%d, '%s', '%s', %d, %d)''' % (int(from_uid), from_ip, from_port, int(to_uid), 0)

    print(sql)

    try:
      cursor.execute(sql)
      self.conn.commit()
      self.update_user_status(from_uid)
    except Exception as e:
      return False, str(e)
    return True, ''

  def fetch_connection_info(self, cid):
    """
    获取连接状态
    """

    sql = 'SELECT * FROM CONNECTIONS WHERE id = ?'

    try:
      res = self.conn.execute(sql, cid).fetchone()
      print(res)
      return True, res
    except Exception as e:
      return False, str(e)

  def reply_connection(self, cid, to_port, to_ip):
    """
    应答连接
    """
    sql = 'UPDATE CONNECTIONS SET to_port = "%s", to_ip = "%s", status = %d WHERE cid = %d' % (to_port, to_ip, 1, cid)

    print(sql)

    try:
      res = self.conn.execute(sql).fetchone()
      print(res)
      return True, res
    except Exception as e:
      return False, str(e)

  def try_connection(self, cid):
    """
    尝试连接
    """
    sql = 'UPDATE CONNECTIONS SET status = status + 1 WHERE cid = %d' % cid

    print(sql)

    try:
      res = self.conn.execute(sql).fetchone()
      print(res)
      return True, res
    except Exception as e:
      return False, str(e)
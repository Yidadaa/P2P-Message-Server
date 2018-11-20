from flask import Flask, request, url_for, send_file
from werkzeug.utils import secure_filename
import json, os

from utils import get_path_of, hash_file_name
from db import DB

UPLOAD_FOLDER_NAME = 'img/'

UPLOAD_FOLDER = get_path_of(UPLOAD_FOLDER_NAME)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__, static_folder=UPLOAD_FOLDER_NAME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = DB()

def check_filename(filename):
  """
  检查文件名是否合法
  """
  print(filename)
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/signin', methods=['POST'])
def register_user():
  status, res = db.add_user({
    'name': request.form['username'],
    'password': request.form['password']
  })
  error = {
    'success': False
  }
  if status is True:
    return json.dumps({ 'success': status, 'userid': res })
  else:
    error['error_msg'] = res
    return json.dumps(error)

@app.route('/login', methods=['POST'])
def login():
  status, res = db.check_user({
    'name': request.form['username'],
    'password': request.form['password']
  })
  error = {
    'success': False
  }

  print(status, res)

  if status is True:
    return json.dumps({ 'success': status, 'user': res })
  else:
    return json.dumps(error)

@app.route('/messages', methods=['post'])
def get_messages():
  status, res = db.collect_messages(request.form['userid'])
  error = {
    'success': False
  }

  # print(status, res)

  if status is True:
    return json.dumps({ 'success': status, 'data': res })
  else:
    return json.dumps(error)

@app.route('/contacts', methods=['post'])
def get_contacts():
  status, res = db.collect_contacts(request.form['userid'])
  error = {
    'success': False
  }

  print(status, res)

  if status is True:
    return json.dumps({ 'success': status, 'data': res })
  else:
    return json.dumps(error)

@app.route('/send', methods=['post'])
def send_messages():
  status, res = db.add_message(
    request.form['from_userid'],
    request.form['to_userid'],
    request.form['content'],
    request.form['ts'])
  error = {
    'success': False
  }

  print(status, res)

  if status is True:
    return json.dumps({ 'success': status, 'id': res })
  else:
    return json.dumps(error)

@app.route('/upload-img', methods=['post'])
def upload_img():
  """
  处理上传的图片
  """
  error = {
    'success': False
  }
  if 'img' not in request.files:
    error['msg'] = 'No file to be uploaded'
    return json.dumps(error)

  file = request.files['img']
  if file and check_filename(file.filename):
    filename = secure_filename(file.filename)
    filename = hash_file_name(filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    print(filename)
    return json.dumps({
      'success': True,
      'img_url': filename
    })
  else:
    error['msg'] = 'Unallowed file'
    return json.dumps(error)

@app.route('/avatar/<filename>', methods=['GET'])
def server_img(filename):
  if filename and check_filename(filename):
    return send_file(get_path_of(UPLOAD_FOLDER_NAME + filename))
  else:
    return 'error'

@app.route('/update-user', methods=['POST'])
def update_user():
  status, res = db.update_user_info(json.loads(request.form['user_info']), int(request.form['userid']))

  print(status, res)

  if status:
    return json.dumps({ 'success': True })
  else:
    return json.dumps({ 'success': False, 'msg': res })

if __name__ == "__main__":
    app.run(debug=True, port=80, host='0.0.0.0')

@app.route('/update-connection/<rtype>', methods=['POST'])
def update_connection(rtype):
  form = request.form
  status = False
  res = {
    'success': False,
    'data': []
  }

  if rtype == 'start':
    # 发起方发起连接
    status, data = db.start_connection(
      form['from_uid'],
      request.remote_addr,
      form['from_port'],
      form['to_uid']
    )
  elif rtype == 'reply':
    # 对方同意连接
    status, data = db.reply_connection(
      form['cid'],
      form['to_port'],
      request.remote_addr,
    )
  elif rtype == 'fetch':
    # 获取连接状态
    status, data = db.fetch_connection_info(form['cid'])
  elif rtype == 'try':
    # 双方尝试连接
    status, data = db.try_connection(form['cid'])

  res['success'] = status
  res['data'] = data
  return res
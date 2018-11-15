from flask import Flask, request
from db import DB
import json

app = Flask(__name__)
db = DB()

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

if __name__ == "__main__":
    app.run(debug=True, port=80, host='0.0.0.0')
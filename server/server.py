from flask import Flask
from db import DB

app = Flask(__name__)
db = DB()

@app.route('/register')
def register_user():
  status, res = db.add_user({ 'name': 'test' })
  return 'ok' + str(status) + str(res)

if __name__ == "__main__":
    app.run(debug=True, port=80, host='0.0.0.0')
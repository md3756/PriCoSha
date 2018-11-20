from flask import Flask, render_template
import pymysql
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello"

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')


if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)

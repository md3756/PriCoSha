from flask import Flask, render_template
import pymysql
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')
    
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/select_blogger')
def select_blogger():
    return render_template('select_blogger.html')

@app.route('/show_posts')
def show_posts():
    return render_template('show_posts.html')

if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)

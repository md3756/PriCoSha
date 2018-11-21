from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

app = Flask(__name__)

#WAMP server
#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       port=3308,
                       password = 'root',
                       db='pricosha',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')


#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['email']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM person WHERE email = %s and password = SHA2(%s,256)'
    cursor.execute(query, (username, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['email'] = username
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or email'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['email']
    password = request.form['password']
    fname = request.form['fname']
    lname = request.form['lname']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM person WHERE email = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO person VALUES(%s, SHA2(%s,256), %s, %s)'
        cursor.execute(ins, (username, password, fname, lname))
        conn.commit()
        cursor.close()
        return render_template('index.html')


@app.route('/home')
def home():
    user = session['email']
    cursor = conn.cursor();
    query = 'SELECT * FROM contentitem WHERE post_time > DATE_SUB(NOW(), INTERVAL 24 HOUR) AND is_pub = True ORDER BY item_id DESC'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=user, posts=data)

@app.route('/logout')
def logout():
    session.pop('email')
    return redirect('/')

app.secret_key = 'some key that you will never guess'


if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)

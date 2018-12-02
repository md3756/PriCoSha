from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

app = Flask(__name__)

#WAMP server
#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password = '',
                       db='pricosha',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    cursor = conn.cursor()
    query = 'SELECT * FROM contentitem WHERE post_time > DATE_SUB(NOW(), INTERVAL 24 HOUR) AND is_pub = True ORDER BY item_id DESC'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('index.html', posts=data)

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
    query = 'SELECT * FROM contentitem WHERE email_post = %s ORDER BY item_id DESC'
    cursor.execute(query, (user))
    data1 = cursor.fetchall()
    query = 'SELECT fname, lname FROM person WHERE email = %s'
    cursor.execute(query, (user))
    name = cursor.fetchone()
    query = 'SELECT * FROM tag WHERE email_tagged = %s AND status = "FALSE" ORDER BY tagtime DESC'
    cursor.execute(query, (user))
    data2 = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=user, posts=data, posts_user = data1, name=name, tags = data2)

@app.route('/post', methods=['GET','POST'])
def post():
    post = request.form['post_name']
    is_pub = int(request.form['public'])
    user = session['email']
    cursor = conn.cursor();
    if(is_pub == 1):
        ins = 'INSERT INTO contentitem VALUES(NULL, %s, NOW(), NULL, %s, TRUE)'
    else:
        ins = 'INSERT INTO contentitem VALUES(NULL, %s, NOW(), NULL, %s, FALSE)'
    cursor.execute(ins, (user, post))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))

@app.route('/show_posts', methods=['GET','POST'])
def show_posts():
    item = request.form['post']
    session['item_id'] = item
    cursor = conn.cursor();
    ins = 'SELECT * FROM contentitem WHERE item_id = %s'
    cursor.execute(ins, (item))
    data = cursor.fetchall()
    ins = 'SELECT fname, lname, person.email FROM tag JOIN person ON tag.email_tagged = person.email WHERE item_id = %s AND status = "TRUE"'
    cursor.execute(ins, (item))
    data1 = cursor.fetchall()
    cursor.close()
    return render_template('show_posts.html', post = data, tags = data1)

@app.route('/tag', methods=['GET','POST'])
def tag():
    tagger = session['email']
    tagged = request.form['friendTag']
    item = session['item_id']
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM tag WHERE email_tagged = %s AND item_id = %s'
    cursor.execute(query, (tagged, item))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then tag exists
        error = "This tag already exists"
        return redirect(url_for('home'))
    else:
        if (tagger == tagged):
            ins = 'INSERT INTO tag VALUES(%s, %s, %s, "TRUE", NOW())'
        else:
            ins = 'INSERT INTO tag VALUES(%s, %s, %s, "FALSE", NOW())'
        cursor.execute(ins, (tagged, tagger, item))
        conn.commit()
        cursor.close()
        return redirect(url_for('home'))



@app.route('/logout')
def logout():
    session.pop('email')
    return redirect('/')

app.secret_key = 'some key that you will never guess'


if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)

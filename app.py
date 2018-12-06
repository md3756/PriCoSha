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
    query = 'SELECT item_id, email_tagger FROM tag WHERE email_tagged = %s AND status = "FALSE" ORDER BY tagtime DESC'
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
    error = None
    if(data):
        #If the previous query returns data, then tag exists
        error = "This tag already exists"
    else:
        if (tagger == tagged):
            ins = 'INSERT INTO tag VALUES(%s, %s, %s, "TRUE", NOW())'
        else:
            ins = 'INSERT INTO tag VALUES(%s, %s, %s, "FALSE", NOW())'
        cursor.execute(ins, (tagged, tagger, item))
        conn.commit()
        cursor.close()
    return redirect(url_for('home'))

@app.route('/tag_group', methods=['GET','POST'])
def tag_group():
    tagger = session['email']
    taggedGroup = request.form['FriendGroupTag']
    owner = request.form['FriendGroupOwner']
    item = session['item_id']
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM belong WHERE owner_email = %s AND fg_name = %s AND email = %s'
    cursor.execute(query, (owner, taggedGroup, tagger))
    data = cursor.fetchone()
    query = 'SELECT email FROM belong WHERE owner_email = %s AND fg_name = %s'
    cursor.execute(query, (owner, taggedGroup))
    data1 = cursor.fetchall()
    query = 'SELECT email_tagged FROM tag WHERE item_id = %s'
    cursor.execute(query, (item))
    data2 = cursor.fetchall()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if not (data):
        error = "This post is not visible to this group"
    else:
        exists = False
        for line in data1:
            for line1 in data2:
                if line['email']== line1['email_tagged']:
                    error = "This person is already tagged or pending a tag"
                    exists = True
            if (tagger == line['email'] and not exists):
                ins = 'INSERT INTO tag VALUES(%s, %s, %s, "TRUE", NOW())'
                cursor.execute(ins, (line['email'], tagger, item))
                conn.commit()
            elif (not exists):
                ins = 'INSERT INTO tag VALUES(%s, %s, %s, "FALSE", NOW())'
                cursor.execute(ins, (line['email'], tagger, item))
                conn.commit()
            exists = False
        cursor.close()
    return redirect(url_for('home'))

@app.route('/friendgroup', methods=['GET','POST'])
def friendgroup():
    user = session['email']
    cursor = conn.cursor();
    ins = 'SELECT friendgroup.fg_name, friendgroup.description FROM friendgroup WHERE owner_email = %s'
    cursor.execute(ins, (user))
    data = cursor.fetchall()
    ins = 'SELECT friendgroup.fg_name, friendgroup.description FROM belong JOIN friendgroup USING (owner_email) WHERE email = %s AND owner_email <> %s'
    cursor.execute(ins, (user, user))
    data1 = cursor.fetchall()
    ins = 'SELECT belong.owner_email, belong.fg_name FROM belong JOIN person USING (email) WHERE email = %s AND status = "FALSE" GROUP BY fg_name'
    cursor.execute(ins, (user))
    data2 = cursor.fetchall()
    return render_template('friendgroup.html', group = data, group1 = data1, members = data2)

@app.route('/create_friendgroup', methods=['GET','POST'])
def create_friendgroup():
    user = session['email']
    description = request.form['description']
    name = request.form['name']
    cursor = conn.cursor();
    query = 'SELECT * FROM friendgroup WHERE owner_email = %s AND fg_name = %s'
    cursor.execute(query, (user, name))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then tag exists
        error = "This group already exists"
    else:
        ins = 'INSERT INTO friendgroup VALUES(%s, %s, %s)'
        cursor.execute(ins, (user, name, description))
        conn.commit()
        ins = 'INSERT INTO belong VALUES(%s, %s, %s)'
        cursor.execute(ins, (user, user, name))
        conn.commit()
        cursor.close()
    return redirect(url_for('friendgroup'))

@app.route('/show_group', methods=['GET','POST'])
def show_group():
    friendgroup = request.form['group']
    session['friendgroup'] = friendgroup
    user = session['email']
    cursor = conn.cursor();
    ins = 'SELECT description FROM friendgroup WHERE owner_email = %s AND fg_name = %s'
    cursor.execute(ins, (user, friendgroup))
    data = cursor.fetchone()
    #double check query!
    ins = 'SELECT fname, lname, person.email FROM belong NATURAL JOIN person WHERE owner_email = %s AND fg_name = %s AND status = "TRUE"'
    cursor.execute(ins, (user, friendgroup))
    data1 = cursor.fetchall()
    cursor.close()
    return render_template('show_group.html', name = friendgroup, info = data, members = data1)

@app.route('/invite_member', methods=['GET','POST'])
def invite_member():
    user = session['email']
    session['owner'] = user
    member = request.form['member']
    name = session['friendgroup']
    cursor = conn.cursor();
    query = 'SELECT * FROM belong WHERE owner_email = %s AND fg_name = %s AND email = %s'
    cursor.execute(query, (user, name, member))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    query = 'SELECT * FROM friendgroup WHERE owner_email = %s AND fg_name = %s'
    cursor.execute(query, (user, name))
    #stores the results in a variable
    data1 = cursor.fetchone()
    query = 'SELECT * FROM person WHERE email = %s'
    cursor.execute(query, (member))
    #stores the results in a variable
    data2 = cursor.fetchone()
    error = None
    if(data):
        #If the previous query returns data, then tag exists
        error = "This member is already in the group"
    elif not (data1):
        error = "This group does not exist"
    elif not (data2):
        error = "This member does not exist"
    else:
        ins = 'INSERT INTO belong VALUES(%s, %s, %s, "FALSE")'
        cursor.execute(ins, (member, user, name))
        conn.commit()
        cursor.close()
    return redirect(url_for('friendgroup'))

@app.route('/tag_ad', methods=['GET','POST'])
def tag_ad():
    item = request.form['item']
    tag = int(request.form['tag'])
    user = session['email']
    cursor = conn.cursor();
    if(tag == 1) :
        ins = 'UPDATE tag SET status = "TRUE" WHERE item_id = %s AND email_tagged = %s'
        cursor.execute(ins, (item, user))
    else:
        ins = 'DELETE FROM tag WHERE item_id = %s AND email_tagged = %s AND status = "FALSE"'
        cursor.execute(ins, (item, user))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))

@app.route('/member_ad', methods=['GET','POST'])
def member_ad():
    #submitting needs work!
    user = session['email']
    name = session['friendgroup']
    owner = session['owner']
    tag = int(request.form['tag'])
    cursor = conn.cursor();
    if(tag == 1) :
        ins = 'UPDATE belong SET status = "TRUE" WHERE email = %s AND owner_email = %s AND fg_name = %s'
        cursor.execute(ins, (user, owner, name))
    else:
        ins = 'DELETE FROM belong WHERE email = %s AND owner_email = %s AND fg_name = % AND status = "FALSE"'
        cursor.execute(ins, (user, owner, name))
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


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

#MAMP server
# conn = pymysql.connect(host='localhost',
#                        user='root',
#                        password = 'root',
#                        port = 8889,
#                        db='pricosha',
#                        charset='utf8mb4',
#                        cursorclass=pymysql.cursors.DictCursor)

#Welcome Page for PriCoSha
@app.route('/')
def index():
    cursor = conn.cursor()
    #Query that gets the data for the public posts in the last 24 hours
    query = 'SELECT * FROM contentitem WHERE post_time > DATE_SUB(NOW(), ' \
            'INTERVAL 24 HOUR) AND is_pub = True ORDER BY item_id DESC'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    #render the template of the specified html page
    return render_template('index.html', posts=data)

#Renders login html file
@app.route('/login')
def login():
    return render_template('login.html')

#Renders register html file
@app.route('/register')
def register():
    return render_template('register.html')



#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs user login info from the forms
    username = request.form['email']
    password = request.form['password']
    cursor = conn.cursor()

    #Query that gets the user login info data
    query = 'SELECT * FROM person WHERE email = %s and password = SHA2(%s,256)'
    cursor.execute(query, (username, password))
    data = cursor.fetchone()
    cursor.close()

    error = None
    if(data):
        #The user exists, so login
        session['email'] = username
        return redirect(url_for('home'))
    else:
        #Error: The user don't exist
        error = 'Invalid login or email'
        return render_template('login.html', error=error)

#Authenticates the registers
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #Grabs user info from the form
    username = request.form['email']
    password = request.form['password']
    fname = request.form['fname']
    lname = request.form['lname']
    cursor = conn.cursor()

    #Gets all data of the user
    query = 'SELECT * FROM person WHERE email = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()
    error = None

    if(data):
        #Error: the user already exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        #Add the user to the database
        ins = 'INSERT INTO person VALUES(%s, SHA2(%s,256), %s, %s)'
        cursor.execute(ins, (username, password, fname, lname))
        conn.commit()
        cursor.close()
        return render_template('index.html')


#Home page after user logins
#Displays public posts, user posts, and awaiting tags
@app.route('/home')
def home():
    return homeError(None)

#Displays home.html in the case where it needs to display an error message or not
def homeError(error):
    user = session['email']
    cursor = conn.cursor();

    #Get all public items, most recent first
    query = 'SELECT * FROM contentitem WHERE is_pub = True ORDER BY ' \
        'post_time DESC'
    cursor.execute(query)
    data = cursor.fetchall()

    #Get all items posted by user, most recent first
    query = 'SELECT * FROM contentitem WHERE email_post = %s ORDER BY ' \
        'post_time DESC'
    cursor.execute(query, (user))
    data1 = cursor.fetchall()

    #Get first name and last name of user
    query = 'SELECT fname, lname FROM person WHERE email = %s'
    cursor.execute(query, (user))
    name = cursor.fetchone()

    #Get item id and email of tagger for pending tags, most recent first
    query = 'SELECT item_id, email_tagger FROM tag WHERE email_tagged = %s ' \
        'AND status = "FALSE" ORDER BY tagtime DESC'
    cursor.execute(query, (user))
    data2 = cursor.fetchall()
    cursor.close()

    if error != None:
        #Render home page if there's no error
        return render_template('home.html', username=user, posts=data, posts_user = data1, name=name, tags = data2, error = error)
    else:
        #Render page with error message if there's an error
        return render_template('home.html', username=user, posts=data, posts_user = data1, name=name, tags = data2)


#Allows user to post text either publicly or privately to friendgroup
#Inserts user's post into database
@app.route('/post', methods=['GET','POST'])
def post():
    user = session['email']
    post = request.form['post_name']
    is_pub = int(request.form['public'])
    file_path = request.form['file_path']
    cursor = conn.cursor();

    if(is_pub == 1 and file_path):
        #Insert public post with file path
        ins = 'INSERT INTO contentitem VALUES(NULL, %s, NOW(), %s, %s, TRUE)'
        cursor.execute(ins, (user, file_path, post))

    elif(is_pub == 0 and file_path):
        #Insert private post with file path
        ins = 'INSERT INTO contentitem VALUES(NULL, %s, NOW(), %s, %s, FALSE)'
        cursor.execute(ins, (user, file_path, post))

    elif(is_pub == 1):
        #Insert public post with no file path
        ins = 'INSERT INTO contentitem VALUES(NULL, %s, NOW(), NULL, %s, TRUE)'
        cursor.execute(ins, (user, post))

    else:
        #Insert private post with no file path
        ins = 'INSERT INTO contentitem VALUES(NULL, %s, NOW(), NULL, %s, FALSE)'
        cursor.execute(ins, (user, post))

    conn.commit()
    cursor.close()
    return homeError(None)


#Allows user to post 1 comments on a post
#Adds comments into the comments table in mySQL
@app.route('/comment', methods=['GET', 'POST'])
def comment():
    user = session['email']
    item = session['item_id']
    comment = request.form['the_comment']
    cursor = conn.cursor()

    #Get all comment data on user's posts
    ins = 'SELECT * FROM comments WHERE item_id = %s AND email = %s'
    cursor.execute(ins, (item, user))
    data1 = cursor.fetchall()

    error = None
    if (data1):
        #Error: A comment is already made on the post
        error = "You already commented on this post :)!"
    else:
        #Add the comment to the post
        ins = 'INSERT INTO comments VALUES(%s, %s, NOW(), %s)'
        cursor.execute(ins, (user, item, comment))
        conn.commit()
        cursor.close()

    return homeError(error)

#Allows user to rate a post once
#Adds rating into the rates table in mySQL
@app.route('/rate', methods=['GET', 'POST'])
def rate():
    user = session['email']
    item = session['item_id']
    emoji = int(request.form['emoji'])
    cursor = conn.cursor()

    #Get all rating data of user's post
    ins = 'SELECT * FROM rate WHERE item_id = %s AND email = %s'
    cursor.execute(ins, (item, user))
    data1 = cursor.fetchall()

    error = None
    if (data1):
        #Error: Can't rate more than once
        error = "You already rated this post! :)"
    else:
        if (emoji == 1):
            #Add heart-eyed emoji for the user's rating
            ins = 'INSERT INTO rate VALUES(%s, %s, NOW(), "😍")'

        elif (emoji == 2):
            #Add crying-laugh emoji for the user's rating
            ins = 'INSERT INTO rate VALUES(%s, %s, NOW(), "😂")'

        elif (emoji == 3):
            #Add thumbs up emoji for the user's rating
            ins = 'INSERT INTO rate VALUES(%s, %s, NOW(), "👍")'

        cursor.execute(ins, (user, item))
        conn.commit()
        cursor.close()

    return homeError(error)

#Shows the posts visible to user since the posts were shared by their friends
#Also shows top rated posts of user's friends and the user which posts that have more than 5 ratings
#The user can link to the top rated post and leave a rating
@app.route('/shared', methods=['GET','POST'])
def shared():
    user = session['email']
    cursor = conn.cursor();

    #Get all data of posts that are shared with user
    query = 'SELECT * FROM belong NATURAL JOIN share NATURAL JOIN ' \
            'contentitem WHERE email = %s AND belong.status = "TRUE" AND email_post <> %s AND is_pub = FALSE'
    cursor.execute(query, (user, user))
    data = cursor.fetchall()

    #Get all data of posts that are rated more than five times and are shared with user
    query = 'SELECT * FROM belong NATURAL JOIN share NATURAL JOIN ' \
            'contentitem NATURAL JOIN (SELECT item_id, COUNT(emoji) AS emo_count FROM rate NATURAL JOIN ' \
            'contentitem GROUP BY item_id HAVING emo_count > 5) AS top_rated WHERE email = %s AND belong.status = "TRUE"'
    cursor.execute(query, (user))
    data2 = cursor.fetchall()

    cursor.close()
    return render_template('shared_posts.html', posts=data, emoji1=data2)

#Shows the details of the user's post
#Implements features such as edit post, share post, comment, rate, and tagging of a person or group
@app.route('/show_posts', methods=['GET','POST'])
def show_posts():
    user = session['email']
    item = request.form['post']
    session['item_id'] = item
    cursor = conn.cursor();

    #Get all data on post with item_id
    ins = 'SELECT * FROM contentitem WHERE item_id = %s'
    cursor.execute(ins, (item))
    data = cursor.fetchall()

    #Get first name, last name, and email of user for accepted tags
    ins = 'SELECT fname, lname, person.email FROM tag JOIN person ON ' \
            'tag.email_tagged = person.email WHERE item_id = %s ' \
            'AND status = "TRUE"'
    cursor.execute(ins, (item))
    data1 = cursor.fetchall()

    #Get group name and email of group owner that user belongs to
    ins = 'SELECT DISTINCT fg_name, owner_email FROM belong WHERE email = %s AND status = "TRUE"'
    cursor.execute(ins, (user))
    data2 = cursor.fetchall()

    #Get email and comment on post with item_id for all comments
    ins = 'SELECT email, comment FROM comments WHERE item_id = %s'
    cursor.execute(ins, (item))
    data3 = cursor.fetchall()

    #Get email and emoji of post with item_id for all ratings
    ins = 'SELECT email, emoji FROM rate WHERE item_id = %s'
    cursor.execute(ins, (item))
    data4 = cursor.fetchall()

    cursor.close()
    return render_template('show_posts.html', post = data, tags = data1,
            groups = data2, comments = data3, ratings = data4)



#Shows the details of the posts shared to user privately
#Implements features such as comment, rate, and tagging of a person or group
@app.route('/show_visibleposts', methods=['GET','POST'])
def show_visibleposts():
    user = session['email']
    item = request.form['post']
    poster = request.form['poster']
    session['item_id'] = item
    session['poster'] = poster
    cursor = conn.cursor();

    #Get all data of post with item_id
    ins = 'SELECT * FROM contentitem WHERE item_id = %s'
    cursor.execute(ins, (item))
    data = cursor.fetchall()

    #Get first name, last name, and email of person for accepted tags
    ins = 'SELECT fname, lname, person.email FROM tag JOIN person ON ' \
            'tag.email_tagged = person.email ' \
            'WHERE item_id = %s AND status = "TRUE"'
    cursor.execute(ins, (item))
    data1 = cursor.fetchall()

    #Selects the groups that the owner of the post and the user share/ are both a member of
    ins = 'SELECT DISTINCT fg_name, owner_email FROM belong AS b WHERE ' \
            'email = %s AND status = "TRUE" AND (fg_name, owner_email) in ' \
            '(SELECT fg_name, owner_email FROM belong WHERE email = %s ' \
            'AND fg_name = b.fg_name AND ' \
            'owner_email = b.owner_email AND status = "TRUE")'
    cursor.execute(ins, (poster, user))
    data2 = cursor.fetchall()

    #Get email and comment on post with item_id for all comments
    ins = 'SELECT email, comment FROM comments WHERE item_id = %s'
    cursor.execute(ins, (item))
    data3 = cursor.fetchall()

    #Get email and emoji on post with item_id for all ratings
    ins = 'SELECT email, emoji FROM rate WHERE item_id = %s'
    cursor.execute(ins, (item))
    data4 = cursor.fetchall()

    cursor.close()
    return render_template('show_visibleposts.html', post = data,
        tags = data1, groups = data2, comments = data3, ratings = data4)

#Shows the details of the public posts
#Implements features such as comment, rate, and tagging of a person
@app.route('/show_publicposts', methods=['GET','POST'])
def show_publicposts():
    user = session['email']
    item = request.form['post']
    poster = request.form['poster']
    session['item_id'] = item
    session['poster'] = poster
    cursor = conn.cursor()

    #Get all data of post with item_id
    ins = 'SELECT * FROM contentitem WHERE item_id = %s'
    cursor.execute(ins, (item))
    data = cursor.fetchall()

    #Get first name, last name, and email of person for accepted tags
    ins = 'SELECT fname, lname, person.email FROM tag JOIN person ON ' \
        'tag.email_tagged = person.email WHERE item_id = %s AND status = "TRUE"'
    cursor.execute(ins, (item))
    data1 = cursor.fetchall()

    #Get email and comment of post with item_id for all comments
    ins = 'SELECT email, comment FROM comments WHERE item_id = %s'
    cursor.execute(ins, (item))
    data2 = cursor.fetchall()

    #Get email and emoji of post with item_id for all rating
    ins = 'SELECT email, emoji FROM rate WHERE item_id = %s'
    cursor.execute(ins, (item))
    data3 = cursor.fetchall()
    cursor.close()

    return render_template('show_publicposts.html', post = data, tags = data1,
            comments = data2, ratings = data3)

#Edits the user's post if given inputs
@app.route('/edit_post', methods=['GET','POST'])
def edit_post():
    item = session['item_id']
    item_name = request.form['item_name']
    file_path = request.form['file_path']
    cursor = conn.cursor();

    if (item_name):
        #Change name of post with item_id
        ins = 'UPDATE contentitem SET item_name = %s WHERE item_id = %s'
        cursor.execute(ins, (item_name, item))
        conn.commit()

    if (file_path):
        #Change file path of post with item_id
        ins = 'UPDATE contentitem SET file_path = %s WHERE item_id = %s'
        cursor.execute(ins, (file_path, item))
        conn.commit()

    if(item_name or file_path):
        #Change post time to now if the post is edited
        ins = 'UPDATE contentitem SET post_time = NOW() WHERE item_id = %s'
        cursor.execute(ins, (item))
        conn.commit()

    cursor.close()
    return redirect(url_for('home'))

#Share the post of the user to the groups that it belongs to
@app.route('/share_post', methods=['GET','POST'])
def share_post():
    item = session['item_id']
    group = request.form['group']
    owner = request.form['owner']
    cursor = conn.cursor()

    #Get all data of post that is shared with the group
    query = 'SELECT * FROM share WHERE item_id = %s AND ' \
            'owner_email = %s AND fg_name = %s'
    cursor.execute(query, (item, owner, group))
    data = cursor.fetchone()
    #To check if the specified friendgroup exists
    query = 'SELECT * FROM friendgroup WHERE owner_email = %s AND fg_name = %s'
    cursor.execute(query, (owner, group))
    data1 = cursor.fetchall()

    error = None
    if(data):
        #Error: The post was already shared with the group
        error = "This post was already shared to this group"
    if not (data1):
        #if no data is returned, then group does not exists
        error = "This group does not exist"
    else:
        #Share post with the group
        ins = 'INSERT INTO share VALUES(%s, %s, %s)'
        cursor.execute(ins, (owner, group, item))
        conn.commit()
        cursor.close()

    return homeError(error)

#Tags individual people in a post if the post is visible to the to-be tagged person
@app.route('/tag', methods=['GET','POST'])
def tag():
    user = session['email']
    tagged = request.form['friendTag']
    item = session['item_id']
    cursor = conn.cursor()

    #Get all data for person-tagged's tag on the post with item_id
    query = 'SELECT * FROM tag WHERE email_tagged = %s AND item_id = %s'
    cursor.execute(query, (tagged, item))
    data = cursor.fetchone()

    #Checks if the post with specified item_id was shared to the person being tagged
    query = 'SELECT * FROM belong NATURAL JOIN share NATURAL JOIN ' \
            'contentitem WHERE item_id = %s AND email = %s AND belong.status = "TRUE"'
    cursor.execute(query, (item, tagged))
    data1 = cursor.fetchone()

    #Get all data for post with item_id that is public
    query = 'SELECT * FROM contentitem WHERE item_id = %s AND is_pub = TRUE'
    cursor.execute(query, (item))
    data2 = cursor.fetchone()

    #Get all data for tagged user, check if the tagged person exists
    query = 'SELECT * FROM person WHERE email = %s'
    cursor.execute(query, (tagged))
    data3 = cursor.fetchall()
    error = None

    if not (data3):
        #Error: The person tagged does not exist
        error = "This person that you are trying to tag does not exist"

    elif(data):
        #Error: email_tagged is already tagged on the post
        error = "This tag already exists"

    else:
        #Checks if the post is public or visible to the person tagged
        if(not data2 and not data1):
            #Error: The post is not visible to the person tagged
            error = "This post is not visible to person tagged"

        else:
            if (user == tagged):
                #Automatically accept tag if user is tagging themself
                ins = 'INSERT INTO tag VALUES(%s, %s, %s, "TRUE", NOW())'

            else:
                #Send tag request to person tagged for tag pending
                ins = 'INSERT INTO tag VALUES(%s, %s, %s, "FALSE", NOW())'

            cursor.execute(ins, (tagged, user, item))
            conn.commit()
            cursor.close()

    return homeError(error)

#Tags all the members of a group in the post if the post is visible to the to-be tagged group
@app.route('/tag_group', methods=['GET','POST'])
def tag_group():
    user = session['email']
    taggedGroup = request.form['FriendGroupTag']
    owner = request.form['FriendGroupOwner']
    item = session['item_id']
    cursor = conn.cursor()

    #To checks if the post is shared with the specified friend group
    query = 'SELECT * FROM share WHERE owner_email = %s ' \
            'AND fg_name = %s AND item_id = %s'
    cursor.execute(query, (owner, taggedGroup, item))
    data = cursor.fetchone()

    #Get email of all members in the specified group
    query = 'SELECT email FROM belong WHERE owner_email = %s AND fg_name = %s AND status = "TRUE"'
    cursor.execute(query, (owner, taggedGroup))
    data1 = cursor.fetchall()

    #Get email of everyone that is tagged in post with item_id
    query = 'SELECT email_tagged FROM tag WHERE item_id = %s'
    cursor.execute(query, (item))
    data2 = cursor.fetchall()

    error = None
    if not (data):
        #If nothing is returned, then the post is not visible or shared with group since it is public
        error = "This post is not visible to this group or post is public"
    else:
        #variable to check if person already tagged
        exists = False
        #Loop through email of all members in tagged group
        for line in data1:
            #Loop through email of everyone that is tagged in post with item_id
            for line1 in data2:
                if line['email'] == line1['email_tagged']:
                    #Error: The person is already tagged or have a tag pending for this post
                    error = "This person is already tagged or pending a tag"
                    exists = True

            if (user == line['email'] and not exists):
                #The user in the group is not yet tagged on the post
                ins = 'INSERT INTO tag VALUES(%s, %s, %s, "TRUE", NOW())'
                cursor.execute(ins, (line['email'], user, item))
                conn.commit()

            elif (not exists):
                #The member of the group is not yet tagged on the post
                ins = 'INSERT INTO tag VALUES(%s, %s, %s, "FALSE", NOW())'
                cursor.execute(ins, (line['email'], user, item))
                conn.commit()
            #Reset exist variable for next memmber to the group to be tagged
            exists = False
        cursor.close()

    return homeError(error)

#FriendGroup page
#Displays friendgroups that the user owns and belongs to and awaiting group invites requests
@app.route('/friendgroup', methods=['GET','POST'])
def friendgroup():
    return friendgroupError(None)

#Displays friendgroup.html in the case where it needs to display an error message or not
def friendgroupError(error):
    user = session['email']
    cursor = conn.cursor();

    #Get group name and description of groups that user own
    ins = 'SELECT friendgroup.fg_name, friendgroup.description ' \
            'FROM friendgroup WHERE owner_email = %s'
    cursor.execute(ins, (user))
    data = cursor.fetchall()
    #Gets the group owner and name of the groups that user belongs to
    ins = 'SELECT DISTINCT friendgroup.owner_email, friendgroup.fg_name, ' \
            'friendgroup.description FROM belong NATURAL JOIN friendgroup ' \
            'WHERE email = %s AND owner_email <> %s AND status = "TRUE"'
    cursor.execute(ins, (user, user))
    data1 = cursor.fetchall()
    #Gets the pending group invites for the user
    ins = 'SELECT belong.owner_email, belong.fg_name FROM belong JOIN ' \
            'person USING (email) WHERE email = %s AND ' \
            'status = "FALSE" GROUP BY fg_name,owner_email'
    cursor.execute(ins, (user))
    data2 = cursor.fetchall()
    cursor.close()

    if error != None:
        return render_template('friendgroup.html', group = data, group1 = data1, members = data2, error = error)
    else:
        return render_template('friendgroup.html', group = data, group1 = data1, members = data2)

@app.route('/create_friendgroup', methods=['GET','POST'])
def create_friendgroup():
    user = session['email']
    description = request.form['description']
    name = request.form['name']
    cursor = conn.cursor();
    #To check if the friendgroup with the specified name and owner
    query = 'SELECT * FROM friendgroup WHERE owner_email = %s ' \
            'AND fg_name = %s'
    cursor.execute(query, (user, name))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the query returns data, then group exists
        error = "This group already exists"
    else:
        #Insert friendgroup values if friendgroup can be created
        ins = 'INSERT INTO friendgroup VALUES(%s, %s, %s)'
        cursor.execute(ins, (user, name, description))
        conn.commit()
        #Insert the owner in belong table to show that they belong to the group
        ins = 'INSERT INTO belong VALUES(%s, %s, %s, "TRUE")'
        cursor.execute(ins, (user, user, name))
        conn.commit()
        cursor.close()
    return friendgroupError(error)

#Shows the details of the friendgroup that the user owns such as the members and description
@app.route('/show_group', methods=['GET','POST'])
def show_group():
    friendgroup = request.form['group']
    session['friendgroup'] = friendgroup
    user = session['email']
    cursor = conn.cursor();
    #Gets the description of the specified friendgroup owner and name
    ins = 'SELECT description FROM friendgroup WHERE ' \
            'owner_email = %s AND fg_name = %s'
    cursor.execute(ins, (user, friendgroup))
    data = cursor.fetchone()
    #Gets the first name, last name and emails of the members of the specified friendgroup
    ins = 'SELECT fname, lname, person.email FROM belong NATURAL JOIN ' \
        'person WHERE owner_email = %s AND fg_name = %s AND status = "TRUE"'
    cursor.execute(ins, (user, friendgroup))
    data1 = cursor.fetchall()
    cursor.close()
    return render_template('show_group.html', name = friendgroup,
            info = data, members = data1)

#Show the details of the group that the
@app.route('/show_belonggroup', methods=['GET','POST'])
def show_belonggroup():
    friendgroup = request.form['group']
    session['friendgroup'] = friendgroup
    owner = request.form['owner']
    cursor = conn.cursor();
    #Gets the owner email and description from the groups that user belongs to
    ins = 'SELECT owner_email, description FROM friendgroup ' \
            'WHERE owner_email = %s AND fg_name = %s'
    cursor.execute(ins, (owner, friendgroup))
    data = cursor.fetchone()
    #Gets the first name, last name and emails of the members of the group that the users belong to
    ins = 'SELECT fname, lname, person.email FROM belong ' \
            'NATURAL JOIN person WHERE owner_email = %s ' \
            'AND fg_name = %s AND status = "TRUE"'
    cursor.execute(ins, (owner, friendgroup))
    data1 = cursor.fetchall()
    cursor.close()
    return render_template('show_belonggroup.html',
            name = friendgroup, info = data, members = data1)

#Accept and decline pending tag requests for user
@app.route('/tag_ad', methods=['GET','POST'])
def tag_ad():
    item = request.form['item']
    tag = int(request.form['tag'])
    user = session['email']
    cursor = conn.cursor();
    #tag == 1 indicates that the tag was accepted
    if(tag == 1) :
        #Sets the status attribute in tag to True to show the tag was approved
        ins = 'UPDATE tag SET status = "TRUE" WHERE ' \
            'item_id = %s AND email_tagged = %s'
        cursor.execute(ins, (item, user))
    else:
        #Deletes the tag from the tag table since the tag was declined
        ins = 'DELETE FROM tag WHERE item_id = %s AND ' \
            'email_tagged = %s AND status = "FALSE"'
        cursor.execute(ins, (item, user))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))

#Accept and decline a friendgroup invite for user
@app.route('/member_ad', methods=['GET','POST'])
def member_ad():
    user = session['email']
    name = session['friendgroup']
    owner = session['owner']
    tag = int(request.form['tag'])
    cursor = conn.cursor();
    if(tag == 1) :
        #Sets the status attribute in belong to True to show the invite was approved
        ins = 'UPDATE belong SET status = "TRUE" WHERE email = %s ' \
                'AND owner_email = %s AND fg_name = %s'
        cursor.execute(ins, (user, owner, name))
    else:
        #Deletes the invite request from the belong table since the invite was declined
        ins = 'DELETE FROM belong WHERE email = %s AND ' \
            'owner_email = %s AND fg_name = %s AND status = "FALSE"'
        cursor.execute(ins, (user, owner, name))
    conn.commit()
    cursor.close()
    return redirect(url_for('friendgroup'))

#Invites members to the specified friendgroup
@app.route('/invite_member', methods=['GET','POST'])
def invite_member():
    user = session['email']
    session['owner'] = user
    fname = request.form['fmember']
    lname  = request.form['lmember']
    group = session['friendgroup']
    cursor = conn.cursor();
    #To check all the people belonging to a specified friendgroup
    query = 'SELECT * FROM belong NATURAL JOIN person WHERE ' \
            'owner_email = %s AND fg_name = %s AND fname = %s AND lname = %s'
    cursor.execute(query, (user, group, fname, lname))
    data = cursor.fetchall()
    #To check if the specified friendgroup exists
    query = 'SELECT * FROM friendgroup WHERE owner_email = %s AND fg_name = %s'
    cursor.execute(query, (user, group))
    data1 = cursor.fetchall()
    #To check if a person exists
    query = 'SELECT * FROM person WHERE fname = %s AND lname = %s'
    cursor.execute(query, (fname, lname))
    data2 = cursor.fetchall()

    error = None
    lst = []
    #Adds the people belonging to the specified group to the list lst
    for invited in data:
        lst.append(invited["email"])
    if not (data1):
        #if no data is returned, then group does not exists
        error = "This group does not exist"
    elif not (data2):
        #if no data is returned, then person does not exists
        error = "This person does not exist"
    else:
        for name in data2:
            #if there is no one with the specified name that has been invited to the group, add the member
            if len(data) == 0:
                ins = 'INSERT INTO belong VALUES(%s, %s, %s, "FALSE")'
                cursor.execute(ins, (name["email"], user, group))
            else:
                #Otherwise, there are people with the name that have been invited, but it could be the same person or different person with the same name
                if name['email'] not in lst:
                    error = None
                    ins = 'INSERT INTO belong VALUES(%s, %s, %s, "FALSE")'
                    cursor.execute(ins, (name["email"], user, group))
                    conn.commit()
                else:
                    #Shows error if the person with the specified name
                    error = name['fname'] + " " + name['lname'] + "(" + name['email'] + ") is already invited or a member"
        cursor.close()
    return friendgroupError(error)

#Logs out of session of the user
@app.route('/logout')
def logout():
    session.pop('email')
    return redirect('/')

#Session key
app.secret_key = 'some key that you will never guess'

#Runs program
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)

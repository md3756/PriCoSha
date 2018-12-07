# **PriCoSha**

### **Project Description**
PriCoSha is a system of privately sharing content items among groups of people. PriCoSha gives users somewhat more privacy than many content sharing sites by giving them more detailed control over who can see which content items they post and more control over whether other people can tag content items with a user’s personal information. Users are able to log in, post and view content items posted by others, and tag content items with emails of people referred to in the content items if given permission. PriCoSha was created using Flask and MySQL and using pymysql to connect to the database.

### **Features**

##### View public content
  Shows users the item_id, email_post, post_time, file_path and item_name of the public content items that were posted within the last 24 hours. This is shown on the 'Welcome to PriCoSha' page (index.html) in which the user can login or register as well as the Home page (home.html) after the user logs in.

##### Login

  Users enter email and passwords. The form requires the user to input an appropriate email in the email textbox. PriCoSha checks whether the hash of password matches stored hashed password for that email and initiates a session, stores email and other relevant data in session variables, and redirects to the home page. Otherwise, the user is informed by PriCoSha informs the user that the login failed and does not initiate the session. There is a link on the 'Welcome to PriCoSha' page (index.html) for logging in that will redirect the user to a login page.

##### View shared content items and info about them

  Shows users the item_id, email_post, post_time, file_path and item_name of content items that are visible to them, arranged in reverse chronological order which is shown on the Shared/Top Rated Posts Page (shared_posts.html)

##### Manage Tags

  Shows users relevant data about content items that have proposed tags of user. Users can choose to accept or decline a tag, or not make a decision which is shown on the Home page at the bottom after the user logs in (home.html)

##### Post a content item

  User enters relevant data such as the post name and file_path as well as designates whether the content item is public or private. The post is automatically assigned a unique item_id and

##### Tag a content item

  Users are able to select content items visible to them and tag to another user with their email

##### Add friend

  User selects an existing FriendGroup that they own and provides first_name and last_name. PriCoSha checks whether there is exactly one person with that name and updates the Belong table to indicate that the selected person is now in the FriendGroup (show_group.html). If there are multiple people with the same name, all of those people are all invited to the group and they can choose whether or not they join the group (friendgroup.html) (Refer to extra feature, group invite). The user is not given the option to add members to a group that they belong to.


### **Extra Features**

##### Adding comments

  Users can add comments about content that is visible to them on the page that shows the details about the post (show_posts.html, show_publicposts.html, show_visibleposts.html). Users are limited to one comment per post. A comments table was created to accommodate the comments for users.

##### Editing posts

  Users who made the post will be able to edit the name of the content item, and file path on the page that shows the details about the post (show_posts.html). If the post was edited, the post_time is altered to be the current time and date.

##### Create FriendGroup

  Users can create a Friend Group and add members/invite members to their groups on the FriendGroup page (friendgroup.html). The groups that the user owns appears on the top of the FriendGroup page. If the user clicks on the friendgroup that they own, they can view the members and have the option of adding members on the page that shows the details about the group (show_posts.html).

##### Group invite

  The owner of the group can send invites/requests a member to join their group. Users can accept, decline or ignore the invite to join the group on the FriendGroup page (friendgroup.html). Users have to accept requests from the owner of the group to be a member of the group. An attribute known as status was added to the belong table to keep track of the pending group invites/members and members of the group.

##### Tagging a FriendGroup

  Users can tag all members in a FriendGroup that they belong to in a post that they posted (show_posts.html). For a post that is shared to them, the user can tag all the members of the group(s) that the owner of the post and the user share (show_visibleposts.html). It is similar to tagging multiple users. It checks if the member has already been tagged and if not, the tag requests are sent except self tagging since the user can tag themselves. The user is not given the option of tagging groups on public posts page, but the user can tag individual people (show_publicposts.html).

##### Rating posts

  Users are able to rate posts with various emojis on the on the page that shows the details about the post (show_posts.html, show_publicposts.html, show_visibleposts.html).

##### Top rated posts among friends

  The top rated posts or the posts with greater than 5 emoji rates are displayed (shared_posts.html). It shows the number of ratings the top rated post possesses. The user is linked to the top rated posts (show_visibleposts.html) so the user can see the comments and ratings left on the post.

##### Register

    Users can register themselves with an unique email; otherwise, an error message will appear. The form requires the user to input an appropriate email in the email textbox, a password as well as their first name and last name (register.html).

### **Member Contributions**
Mithila: Adding comments, Rating posts, CSS features
Daisy: Group Invite, Add friend, error displaying
Hannah: Editing post, Tagging a Group, Manage tags
Lyanne: Show public content, top rated posts, showing shared content

# **Pricosha**

###**Project Description**
PriCoSha is a system of privately sharing content items among groups of people. PriCoSha gives users somewhat more privacy than many content sharing sites by giving them more detailed control over who can see which content items they post and more control over whether other people can tag content items with a user’s personal information. Users are able to log in, post and view content items posted by others, and tag content items with emails of people referred to in the content items if given permission. PriCoSha was created using Flask and MySQL and using pymysql to connect to the database.

###**Features**
######View public content
  Shows users the item_id, email_post, post_time, file_path and item_name of the public content items that were posted within the last 24 hours.
######Login
  Users enter email and passwords. PriCoSha checks whether the hash of password matches stored password for that email and initiates a session, stores email and other relevant data in session variables, and redirects to the home page. Otherwise, the user is informed by PriCoSha informs the user that the login failed and does not initiate the session.
######View shared content items and info about them
  Shows users the item_id, email_post, post_time, file_path and item_name of content items that are visible to them, arranged in reverse chronological order
######Manage Tags
  Shows users relevant data about content items that have proposed tags of user. Users can choose to accept or decline a tag, or not make a decision
######Post a content item
  User enters relevant data and designates whether the content item is public or private.
######Tag a content item
  Users are able to select content items visible to them and tag to another user with their email
######Add friend
  User selects an existing FriendGroup that they own and provides first_nameand last_name. PriCoSha checks whether there is exactly one person with that name and updates the Belong table to indicate that the selected person is now in the FriendGroup.

###** Extra Features**
######Adding comments
  Users can add comments about content that is visible to them. Users are limited to one comment per post.
######Editing posts
  Users who made the post will be able to edit the name of the content item, file path, and other attributes
######Create FriendGroup
  Users can create a Friend Group and add members
######Pending friend requests
  Users have to accept requests from the owner of the group to be a member of the group.
######Tagging a FriendGroup
  Users can tag all members in a FriendGroup that they belong to.
######Rating posts
  Users are able to rate posts with various emojis and top rated posts are shown.
######Tagging a group
  Users can tag multiple users in a content item can  

###**Member Contributions**

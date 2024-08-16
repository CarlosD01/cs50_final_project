# 4RUMS

**Video Demo:** https://youtu.be/uxkDJXC1pok

## Brief Description

4RUMS is a forum based web application created using Python, Flask, sqlite3, HTML5, and CSS, and was inspired by Reddit. The website consists of 14 HTML template pages, one database, one CSS style page, as well as the main Python application.

## Users and Authentication

In its current state, there are 3 premade accounts that populate users.db: ‘Spider-Man’ - Administrator, ‘Deadpool’ - User, and ‘Wolverine’ - User. The password for each account is ‘123’ for ease of use and cannot be changed in the current state of the application. 

While many features of 4RUMS are open to unauthenticated users, certain features require a user to be logged in with a valid account. To be more specific, unauthenticated users can view the homepage, communities, a post’s page and comments, a user’s profile, as well as the log in/sign up pages. Creating and editing posts and communities, as well as leaving comments on posts, are only available to users logged in with valid accounts. Once a valid account is created, users can access the aforementioned features as well as profile customization. Should a user attempt to access a feature without the correct credentials/authorization, they will be met with a prompt to log in/sign up.

Currently, if all data in users.db is deleted, the first account created will be given administrator privileges. Accounts granted the administrator privilege are decided in app.py and can only be changed in line 48 by adding user ids to the admin_user list; currently the list only contains one id, the integer ‘1’. If an account has an id other than the one(s) listed in admin_user, the account will be given ‘User’ status. All users regardless of their user/administrator statuses have the ability to create communities, create posts, like posts, and leave comments on posts. Users can also edit and delete their own posts and profile, though, username and password change is currently not possible.

## Navigation and Features

Navigation between pages is intuitive and familiar to other social media sites, like Reddit, and allows users to go from page to page seamlessly no matter where they find themselves. When visiting the site initially, users will be taken to the homepage where all posts made to 4RUMS are displayed. In its current state, posts are displayed based on those most recently posted, but in a future update posts will be sorted based on newness and level of user engagement (number of likes and comments). 

If a user wishes to see posts of a certain type, they can visit the communities listed on the left side of the screen by clicking on the link. Users can also navigate back to the homepage by clicking on ‘Home’ listed in the community tab or the ‘4RUMS’ logo in the top left. The communities listed can be referenced when making a post (i.e. posts can be tagged with a certain community), though, the ‘Home’ option is not available as a tag nor can it be deleted.
 
When visiting a community’s page, the user will be greeted by the name and a brief description of the community. Following this overview are all posts which include the community’s tag in order of newness. Regardless of the manner in which a user views a post, a post’s original poster, title, date and time, content, and number of likes are visible. However, visiting a post’s page allows users to leave a comment and view all other comments made. Should a user attempt to visit a page that does not exist, they will be met with an error message and prompted to redirect to the homepage or to try again.

When a user wishes to view or edit their profile, they can click on the profile icon located at the top right of the screen. Here they will find their user dashboard where they can view their profile overview, as well as posts and comments made. It is here users can also add/update their display name, bio, and profile picture, or even delete their account should they choose to.

Should a user want to create a post, they can click on the post icon to the left of the profile icon. Here they will find a form which prompts them for a community tag, a title, and body. While posts cannot be saved as drafts, they can be edited after being posted by visiting the post’s page and clicking on the pen/edit icon.

Similarly, should a user want to create a new community, they can click on the blue community icon on the left side of the screen. They will again find a form and be prompted for a community name and description wherein they can describe the use/focus of the community. As mentioned previously, only accounts with administrator privileges have the ability to edit a community (i.e. the name or description) and can edit communities by clicking on the pen/edit icon to the right of the community’s name.

## Issues with Current Version

A previous version of the application saw issues when deleting posts and the related comments and likes—the post id being referenced in the ‘comments’ and ‘like’ tables became NULL values as there was no longer a valid post id being passed. This issue prevented users from visiting their own, or even other user’s, profile as the HTML template could not properly find and display comments because of the NULL value This issue should now be resolved as the deletion of a post (parent object) will also apply to the associated comments and likes (child objects) via SQLAlchemy’s cascade behavior.

It is also important to mention that, while administrators are the only users with the ability to edit and delete communities, deleting the administrator will cause issues with deleting/editing communities, so it is recommended to delete/edit communities before deleting the administrator account.

## Conclusion

As for other features not currently available, the following were also considered but were ultimately not possible given the timeframe and resources: inter-user interaction (liking/replying to comments and user following), communication (direct messaging), comment editing, and community following. Accessing 4RUMS from different devices may also cause issues with the website as it is mainly intended as a desktop web application. That said, is the hope that a future update will implement these features and improve the overall user experience.

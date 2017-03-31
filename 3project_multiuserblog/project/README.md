# Multi User Blog

This app is a multi user blog similar to Medium where users can log
in and create blog posts as well as interact with other blog posts.

## Motivation

Motivation behind this application was to create an application that
focuses on developing CRUD(create, read, update, delete) alongside functionality. Also, the project supports authentication of users
and demonstrates use of JSON endpoints.

## Code Example

New Post Functionality
```
class NewPost(BlogHandler):

    @user_logged_in
    def get(self, post_id=None):
        self.render("newpost.html", page_title="New Post")

    @user_logged_in
    def post(self, post_id=None):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            username = self.user.name
            p = Post(parent=blog_key(), subject=subject,
                     content=content, owner=username)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render(
                "newpost.html", subject=subject,
                content=content, error=error, page_title="Edit Post")
```
Using third party code

`import webapp2`
`import jinja2`
`from google.appengine.ext import db`

## Source Code:

Make sure you have **python downloaded and installed.**

If not, download [here](https://www.python.org/downloads/)

Follow these steps to get to the source code:

Clone this repository:

[HERE](https://github.com/jovanikimble/Udacity-Nanodegree.git)

`cd` to this directory:

$ Udacity-Nanodegree/3project_multiuserblog/project/blog

The Multi User Blog is live at:

https://multiuserblog-162404.appspot.com
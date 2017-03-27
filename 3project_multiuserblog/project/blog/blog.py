import os
import re
import random
import hashlib
import hmac
from string import letters
from functools import wraps
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret='tupelo'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def user_logged_in(function):

    @wraps(function)
    def wrapper(self, post_id=None):
        if not self.user:
            self.redirect('/login')
            return

        return function(self, post_id)

    return wrapper

def post_exists(function):
    @wraps(function)
    def wrapper(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        if post:
            return function(self, post_id, post)
        else:
            self.error(404)
            return
    return wrapper

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    def user_owns_post(self, post):
        return self.user.name == post.owner

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)


##### user stuff
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u
        return None

##### blog stuff

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    owner = db.StringProperty(required = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        self._id = str(self.key().id())
        return render_str("post.html", p = self)

class Comment(db.Model):
    post_id = db.StringProperty(required = True)
    owner = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class Like(db.Model):
    post_id = db.StringProperty(required =True)
    owner = db.StringProperty(required = True)

class BlogFront(BlogHandler):

    def get(self):
        if self.user:
          # I am logged in here.
          posts = Post.all().order('-created').filter('owner = ', self.user.name)
          other_posts = Post.all().filter('owner != ', self.user.name)
        else:
          posts = Post.all().order('-created')
          other_posts = []

        self.render('front.html', posts = posts, other_posts=other_posts)

class PostPage(BlogHandler):

    @user_logged_in
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        comments = Comment.all().order('-created').filter('post_id = ', post_id)
        post.comments = comments
        post.is_permalink= True
        post.is_liked = False

        if self.user.name != post.owner:
            post.show_like = True
            query = Like.all().filter('post_id =', post_id).filter('owner =', self.user.name)
            results = query.fetch(1)
            if results:
                post.is_liked = True

        self.render("permalink.html", post = post)

    @user_logged_in
    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        comment = self.request.get('comment')
        c = Comment(parent=blog_key(), post_id=post_id,
                    owner = self.user.name, content = comment)
        c.put()
        self.redirect('/blog/%s' % post_id)


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


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(BlogHandler):

    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):

    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')

class Login(BlogHandler):

    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class EditPost(BlogHandler):

    @user_logged_in
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        if not self.user_owns_post(post):
            self.redirect('/')
            return

        self.render(
            "newpost.html", subject = post.subject, content = post.content,
            page_title="Edit Page")

    @user_logged_in
    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        if not self.user_owns_post(post):
            self.redirect('/')
            return

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)

class DeletePost(BlogHandler):

    @user_logged_in
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        if not self.user_owns_post(post):
            self.redirect('/')
            return

        self.render("delete-post.html", subject=post.subject)

    @user_logged_in
    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        if not self.user_owns_post(post):
            self.redirect('/')
            return

        q = self.request.get('q')

        if q == 'y':
            post.delete()
            self.redirect('/')
        else:
            self.redirect('/')

class DeleteComment(BlogHandler):

    @user_logged_in
    def get(self, comment_id):
        key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
        comment = db.get(key)

        if not comment:
            self.redirect('/')
            return

        if comment.owner != self.user.name:
            self.redirect('/blog/%s' % comment.post_id)
            return

        comment.delete()
        self.redirect('/blog/%s' % comment.post_id)

class EditComment(BlogHandler):

    @user_logged_in
    def get(self, comment_id):
        key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
        comment = db.get(key)

        if not comment:
            self.redirect('/')
            return

        c = comment.content

        if comment.owner != self.user.name:
            self.redirect('/blog/%s' % comment.post_id)
            return

        self.render('edit_comment.html', content = c, post_id=comment.post_id)

    @user_logged_in
    def post(self, comment_id):
        key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
        comment = db.get(key)

        if not comment:
            self.redirect('/')
            return

        if comment.owner != self.user.name:
            self.redirect('/blog/%s' % comment.post_id)
            return

        content = self.request.get('content')
        comment.content = content
        comment.put()

        self.redirect('/blog/%s' % comment.post_id)

class LikePost(BlogHandler):

    @user_logged_in
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        query = Like.all().filter('post_id = ', post_id).filter('owner = ', self.user.name)
        results = query.fetch(1)
        if results:
            results[0].delete()
            self.redirect('/blog/%s' % post_id)
            return

        l = Like(parent=blog_key(), post_id=post_id, owner=self.user.name)
        l.put()
        self.redirect('/blog/%s' % post_id)



class Logout(BlogHandler):

    def get(self):
        self.logout()
        self.redirect('/')

class DropAll(BlogHandler):

    def get(self):
        db.delete(Post.all())
        db.delete(User.all())
        self.response.out.write('that worked')

app = webapp2.WSGIApplication([('/', BlogFront),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/dropall', DropAll),
                               ('/edit/([0-9]+)', EditPost),
                               ('/delete/([0-9]+)', DeletePost),
                               ('/delete_comment/([0-9]+)', DeleteComment),
                               ('/edit_comment/([0-9]+)', EditComment),
                               ('/liked/([0-9]+)', LikePost)
                               ],
                              debug=True)

import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)


class Handler(webapp2.RequestHandler):

    def render_template(self, template_name, **kwargs):
        t = jinja_env.get_template(template_name)
        s = t.render(**kwargs)
        self.response.write(s)

class MainHandler(Handler):

    def get(self):
        self.render_template("home.html", name='david', middle='edgar')

class HelloHandler(Handler):

    def get(self):
        self.render_template("home.html", name='jovani', middle='alexandria')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/hello', HelloHandler)
], debug=True)
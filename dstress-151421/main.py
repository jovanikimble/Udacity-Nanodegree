import os
import re
import logging

import webapp2
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):

    def render(self, template, **kw):
        t = jinja_env.get_template(template)
        s = t.render(**kw)
        self.response.out.write(s)

class MainHandler(Handler):

    def get(self):
       self.render("home_page.html")

class VentHandler(Handler):

    def get(self):
        self.render("vent.html")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/vent', VentHandler),
], debug=True)

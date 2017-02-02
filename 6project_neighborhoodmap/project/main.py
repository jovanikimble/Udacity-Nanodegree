from flask import Flask
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask.views import MethodView

import httplib2
import json
from flask import jsonify
from flask import request
from flask import session as login_session
from flask import redirect
import random, string


app = Flask(__name__)

handler = Blueprint('main_handler', __name__)

class MainView(MethodView):
  def get(self):
    context = {}
    return render_template('main.html', context=context)

handler.add_url_rule('/', view_func=MainView.as_view('main_view'))

if __name__ == '__main__':
    app.secret_key = 'boobarismygoobar'
    app.debug = True
    app.register_blueprint(handler, url_prefix='')
    app.run(host='0.0.0.0', port=10000)
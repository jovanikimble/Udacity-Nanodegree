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
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

app = Flask(__name__)

handler = Blueprint('main_handler', __name__)

class MainView(MethodView):
  def get(self):
    context = {}
    return render_template('main.html', context=context)

class GetLocationInfoView(MethodView):

 def get(self):
   title = request.args.get('title')

   creds = json.loads(open('yelp_secrets.json', 'r').read())
   auth = Oauth1Authenticator(**creds)
   yelp_client = Client(auth)

   params = {
       'term': title
   }

   res = yelp_client.search('San Francisco', **params)
   if not res.businesses:
     return jsonify({'status': 'ERROR', 'msg': 'No results found'})

   biz = res.businesses[0]

   biz_item = dict(
     phone=biz.phone,
     rating_img_url=biz.rating_img_url,
     snippet=biz.snippet_text
   )
   return jsonify({'status': 'OK', 'biz': biz_item})

handler.add_url_rule('/get_location_info', view_func=GetLocationInfoView.as_view('yelp_view'))

handler.add_url_rule('/', view_func=MainView.as_view('main_view'))

if __name__ == '__main__':
    app.secret_key = 'boobarismygoobar'
    app.debug = True
    app.register_blueprint(handler, url_prefix='')
    app.run(host='0.0.0.0', port=10000)
from flask import Flask
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from sqlalchemy import create_engine
from flask.views import MethodView

import httplib2
import json
from flask import jsonify
from flask import request
from flask import session as login_session
from flask import redirect
import random
import string

from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from database_setup import engine

app = Flask(__name__)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

handler = Blueprint('main_handler', __name__)


def getUserID(email):
    user = session.query(User).filter_by(email=email).first()
    if not user:
        return None
    return user.id


def createUser(login_session):
    newUser = User(
        name=login_session['name'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    return user.id


class MainView(MethodView):

    def get(self):
        context = {}
        context['login_session'] = login_session

        categories = session.query(Category).all()

        results = session.query(Category, Item).join(Item).order_by(
            Item.added.desc()).limit(10).all()

        context['categories'] = categories
        context['recent_results'] = results
        return render_template('main.html', context=context)


class CatalogJSONView(MethodView):

    def get(self):
        results = session.query(Category, Item).join(Item).order_by(
            Item.added.desc()).all()

        d = {'Items': []}
        for category, item in results:
            obj = {
                'CategoryName': category.name,
                'Name': item.name,
                'Description': item.description
            }
            d['Items'].append(obj)

        return jsonify(d)


class CategoryView(MethodView):

    def get(self, category_name):
        context = {}
        context['login_session'] = login_session

        curr_category = session.query(Category).filter_by(
            name=category_name).first()

        if not curr_category:
            return render_template(
                'error.html', msg="Category does not exist :(")

        items_list = session.query(Item).filter_by(
            category_id=curr_category.id)

        categories = session.query(Category).all()
        context['categories'] = categories
        context['category_name'] = category_name
        context['items_list'] = items_list
        return render_template('category.html', context=context)


class ItemView(MethodView):

    def get(self, category_name, item_name):
        context = {}
        context['login_session'] = login_session

        curr_category = session.query(Category).filter_by(
            name=category_name).first()

        if not curr_category:
            return render_template(
                'error.html', msg="Category does not exist :(")

        curr_item = session.query(Item).filter_by(
            name=item_name, category_id=curr_category.id).first()

        if not curr_item:
            return render_template('error.html', msg="Item does not exist :(")

        context['item'] = curr_item
        context['category_name'] = category_name

        return render_template('item.html', context=context)


class AddView(MethodView):

    def get(self):
        if 'email' not in login_session:
            return redirect('/login')

        context = {}
        context['login_session'] = login_session

        categories = session.query(Category).all()
        context['categories'] = categories

        return render_template('add_item.html', context=context)

    def post(self):
        if 'email' not in login_session:
            return redirect('/login')

        user = session.query(User).filter_by(
            email=login_session['email']).first()
        category_name = request.form.get('category', '')
        category = session.query(Category).filter_by(
            name=category_name).first()
        name = request.form.get('name', '')
        description = request.form.get('description', '')

        item = Item(
            user_id=user.id, category_id=category.id, name=name,
            description=description
        )
        session.add(item)
        session.commit()

        return redirect('/catalog/{0}/items'.format(category.name))


class AddCategoryView(MethodView):

    def get(self):
        if 'email' not in login_session:
            return redirect('/login')

        context = {}
        context['login_session'] = login_session

        categories = session.query(Category).all()
        context['categories'] = categories

        return render_template('add_category.html', context=context)

    def post(self):
        if 'email' not in login_session:
            return redirect('/login')

        category_name = request.form.get('name', '')
        category = session.query(Category).filter_by(
            name=category_name).first()

        if category is not None:
            return render_template(
                'error.html',
                msg="That category already exists, create something new")

        new_category = Category(name=category_name)
        session.add(new_category)
        session.commit()

        return redirect('/catalog/{0}/items'.format(category_name))


class EditView(MethodView):

    def get(self, category_name, item_name):
        if 'email' not in login_session:
            return redirect('/login')

        context = {}
        context['login_session'] = login_session

        categories = session.query(Category).all()
        context['categories'] = categories

        category = session.query(Category).filter_by(
            name=category_name).first()
        item = session.query(Item).filter_by(
            name=item_name, category_id=category.id).first()

        if item is None:
            return render_template(
                'error.html',
                msg="Sorry, That item does not exist.")

        user = session.query(User).filter_by(id=item.user_id).first()

        if user is None:
            return render_template(
                'error.html',
                msg='Cannot determine the owner of the item')

        if login_session['email'] != user.email:
            return render_template(
                'error.html',
                msg='You are not allowed to edit this item :(')

        return render_template(
            'edit_item.html', name=item_name,
            category=category_name, description=item.description,
            context=context)

    def post(self, category_name, item_name):
        if 'email' not in login_session:
            return redirect('/login')

        category = request.form.get('category', '')
        name = request.form.get('name', '')
        description = request.form.get('description', '')

        new_category = session.query(Category).filter_by(name=category).first()
        category_object = session.query(Category).filter_by(
            name=category_name).first()
        item = session.query(Item).filter_by(
            name=item_name, category_id=category_object.id).first()

        if item is None:
            return render_template(
                'error.html',
                msg="Sorry, That item does not exist.")

        user = session.query(User).filter_by(id=item.user_id).first()

        if user is None:
            return render_template(
                'error.html',
                msg='Cannot determine the owner of the item')

        if login_session['email'] != user.email:
            return render_template(
                'error.html',
                msg='You are not allowed to edit this item :(')

        item.name = name
        item.description = description
        item.category_id = new_category.id
        session.commit()

        return redirect('/catalog/{0}/items'.format(category))


class DeleteView(MethodView):

    def get(self, category_name, item_name):
        if 'email' not in login_session:
            return redirect('/login')

        context = {}
        context['login_session'] = login_session

        context['item'] = item_name
        context['category'] = category_name

        category = session.query(Category).filter_by(
            name=category_name).first()
        item = session.query(Item).filter_by(
            name=item_name, category_id=category.id).first()

        if item is None:
            return render_template(
                'error.html',
                msg="Sorry, That item does not exist.")

        user = session.query(User).filter_by(id=item.user_id).first()

        if user is None:
            return render_template(
                'error.html',
                msg='Cannot determine the owner of the item')

        if login_session['email'] != user.email:
            return render_template(
                'error.html',
                msg='You are not allowed to delete this item :(')

        return render_template('delete_item.html', context=context)

    def post(self, category_name, item_name):
        if 'name' not in login_session:
            return redirect('/login')

        category = session.query(Category).filter_by(
            name=category_name).first()
        item = session.query(Item).filter_by(
            name=item_name, category_id=category.id).first()

        if item is None:
            return render_template(
                'error.html',
                msg="Sorry, That item does not exist.")

        user = session.query(User).filter_by(id=item.user_id).first()

        if user is None:
            return render_template(
                'error.html',
                msg='Cannot determine the owner of the item')

        if login_session['email'] != user.email:
            return render_template(
                'error.html',
                msg='You are not allowed to delete this item :(')

        session.delete(item)
        session.commit()

        return redirect('/catalog/{0}/items'.format(category_name))


class LoginView(MethodView):

    def get(self):
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        login_session['state'] = state
        context = {}
        context['state'] = state
        return render_template("login.html", context=context)


def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


class LogoutView(MethodView):

    def get(self):
        if 'email' in login_session:
            fbdisconnect()
            del login_session['facebook_id']
            del login_session['name']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            del login_session['provider']
            print('Youve been logged out')
            return redirect('/')
        else:
            print('Already logged out')
            return redirect('/')


class FBConnectView(MethodView):

    def post(self):
        if request.args.get('state') != login_session['state']:
            response = make_response(json.dumps(
                'Invalid state parameter.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        access_token = request.data
        print "access token received %s " % access_token

        app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
            'web']['app_id']
        app_secret = json.loads(
            open('fb_client_secrets.json', 'r').read())['web']['app_secret']
        url = 'https://graph.facebook.com/oauth/access_token?grant_type='
        url += 'fb_exchange_token'
        url += '&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
            app_id, app_secret, access_token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]

        # Use token to get user info from API
        userinfo_url = "https://graph.facebook.com/v2.4/me"
        # strip expire tag from access token
        data = json.loads(result)
        token = 'access_token=' + data['access_token']

        url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % (
            token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        # print "url sent for API access:%s"% url
        # print "API JSON result: %s" % result
        data = json.loads(result)
        print(data)

        if 'error' in data:
            error = data['error'].get(
                'message', 'There was an error connecting to Facebook.')
            resp = {
                'error': error
            }
            return json.dumps(resp)

        login_session['provider'] = 'facebook'
        login_session['name'] = data["name"]
        login_session['email'] = data["email"]
        login_session['facebook_id'] = data["id"]

        # The token must be stored in the login_session in order to properly
        # logout, let's strip out the information before the equals sign in our
        # token
        stored_token = token.split("=")[1]
        login_session['access_token'] = stored_token

        # Get user picture
        url = 'https://graph.facebook.com'
        url += '/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        data = json.loads(result)

        login_session['picture'] = data["data"]["url"]

        # see if user exists
        user_id = getUserID(login_session['email'])
        if not user_id:
            user_id = createUser(login_session)
        login_session['user_id'] = user_id

        output = ''
        output += '<h1>Welcome, '
        output += login_session['name']

        output += '!</h1>'
        output += '<img src="'
        output += login_session['picture']
        output += ' " style = "width: 300px; height: 300px;border-radius:'
        output += '150px;-webkit-border-radius: 150px;-moz-border-radius:'
        output += '150px;"> '
        resp = {
            'result': output
        }
        return json.dumps(resp)


class SetupView(MethodView):

    def get(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(engine)

        u = User(name='Jovani', email='boobar@gmail.com', picture='google.com')
        session.add(u)
        session.commit()

        user = session.query(User).filter_by(name='Jovani').first()
        user_id = user.id

        cat_names = ['Cakeh', 'Skiing', 'Kisses']
        for name in cat_names:
            c = Category(name=name)
            session.add(c)
        session.commit()

        for name in cat_names:
            cat = session.query(Category).filter_by(name=name).first()
            items_names = ['David', 'Skis', 'Lips']
            for item_name in items_names:
                full_name = name + '_' + item_name
                description = 'Description of ' + full_name
                item = Item(user_id=user_id, category_id=cat.id,
                            name=full_name, description=description)
                session.add(item)
        session.commit()

        return "done"


handler.add_url_rule(
    '/catalog/<string:category_name>/items',
    view_func=CategoryView.as_view('category_view'))

handler.add_url_rule(
    '/catalog/<string:category_name>/<string:item_name>',
    view_func=ItemView.as_view('item_view'))

handler.add_url_rule(
    '/setup',
    view_func=SetupView.as_view('setup_view'))

handler.add_url_rule(
    '/catalog/additem',
    view_func=AddView.as_view('add_view'))

handler.add_url_rule(
    '/catalog/addcategory',
    view_func=AddCategoryView.as_view('add_category_view'))

handler.add_url_rule(
    '/catalog/edititem/<string:category_name>/<string:item_name>',
    view_func=EditView.as_view('edit_view'))

handler.add_url_rule(
    '/catalog/<string:category_name>/<string:item_name>/delete',
    view_func=DeleteView.as_view('delete_view'))

handler.add_url_rule('/catalog.json',
                     view_func=CatalogJSONView.as_view('catalog_json_view'))

handler.add_url_rule('/login',
                     view_func=LoginView.as_view('login_view'))

handler.add_url_rule('/logout',
                     view_func=LogoutView.as_view('logout_view'))

handler.add_url_rule('/fbconnect',
                     view_func=FBConnectView.as_view('fb_connect_view'))

handler.add_url_rule('/', view_func=MainView.as_view('main_view'))

if __name__ == '__main__':
    app.secret_key = 'boobarismygoobar'
    app.debug = True
    app.register_blueprint(handler, url_prefix='')
    app.run(host='0.0.0.0', port=5000)

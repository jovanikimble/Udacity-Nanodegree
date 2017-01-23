from flask import Flask
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from sqlalchemy import create_engine
from flask.views import MethodView
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from database_setup import engine

app = Flask(__name__)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

handler = Blueprint('main_handler', __name__)

class MainView(MethodView):

    def get(self):
        context = {}

        categories = session.query(Category).all()
        context['categories'] = categories
        return render_template('main.html',context=context)

class CategoryView(MethodView):

    def get(self, category_name):
        context = {}

        curr_category = session.query(Category).filter_by(
            name=category_name).first()

        if not curr_category:
            return render_template('error.html', msg="Category does not exist :(")

        items_list = session.query(Item).filter_by(
            category_id=curr_category.id)


        categories = session.query(Category).all()
        context['categories'] = categories
        context['category_name'] = category_name
        context['items_list'] = items_list
        return render_template('category.html', context=context)

class ItemView(MethodView):

    def get(self,category_name,item_name):
        context = {}

        curr_category = session.query(Category).filter_by(
            name=category_name).first()

        if not curr_category:
            return render_template('error.html', msg="Category does not exist :(")

        curr_item = session.query(Item).filter_by(
            name=item_name, category_id=curr_category.id).first()

        if not curr_item:
            return render_template('error.html', msg="Item does not exist :(")

        context['item'] = curr_item
        context['category_name'] = category_name

        return render_template('item.html', context=context)

class AddView(MethodView):

    def get(self):
        context ={}

        categories = session.query(Category).all()
        context['categories'] = categories

        return render_template('add_item.html', context=context)

    def post(self):
        user = session.query(User).filter_by(name='Jovani').first()
        category_name = request.form.get('category', '')
        print request.form
        category = session.query(Category).filter_by(name=category_name).first()
        name = request.form.get('name', '')
        description = request.form.get('description', '')

        item = Item(
            user_id=user.id,category_id=category.id, name=name,
            description=description
        )
        session.add(item)
        session.commit()

        return redirect('/catalog/{0}/items'.format(category.name))

class EditView(MethodView):

    def get(self, category_name, item_name):
        context = {}

        categories = session.query(Category).all()
        context['categories'] = categories

        category = session.query(Category).filter_by(name=category_name).first()
        item = session.query(Item).filter_by(name=item_name,category_id=category.id).first()

        return render_template('edit_item.html', name=item_name,
            category=category_name, description=item.description, context=context)

    def post(self, category_name, item_name):

        category = request.form.get('category', '')
        name = request.form.get('name', '')
        description = request.form.get('description', '')

        new_category = session.query(Category).filter_by(name=category).first()
        category_object = session.query(Category).filter_by(name=category_name).first()
        item = session.query(Item).filter_by(name=item_name,category_id=category_object.id).first()

        item.name = name
        item.description = description
        item.category_id = new_category.id
        session.commit()

        return redirect('/catalog/{0}/items'.format(category))

class DeleteView(MethodView):

    def get(self,category_name, item_name):
        context = {}

        context['item'] = item_name
        context['category'] = category_name

        return render_template('delete_item.html', context=context)

    def post(self, category_name, item_name):

        category = session.query(Category).filter_by(name=category_name).first()
        item = session.query(Item).filter_by(name=item_name,
            category_id=category.id).first()

        session.delete(item)
        session.commit()

        return redirect('/catalog/{0}/items'.format(category_name))


class SetupView(MethodView):

    def get(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(engine)

        u =User(name='Jovani')
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
                item = Item(user_id=user_id,category_id=cat.id,name=full_name, description=description)
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
    '/catalog/edititem/<string:category_name>/<string:item_name>',
    view_func=EditView.as_view('edit_view'))

handler.add_url_rule(
    '/catalog/<string:category_name>/<string:item_name>/delete',
    view_func=DeleteView.as_view('delete_view'))

handler.add_url_rule('/', view_func=MainView.as_view('main_view'))

if __name__ == '__main__':
    app.debug = True
    app.register_blueprint(handler, url_prefix='')
    app.run(host='0.0.0.0', port=5000)
from flask import Flask
from flask import Blueprint
from flask import render_template
from sqlalchemy import create_engine
from flask.views import MethodView
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

handler = Blueprint('main_handler', __name__)

class RestaurantView(MethodView):

    def get(self, restaurant_id):
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
        output = ''
        for i in items:
            output += i.name
            output += '</br>'
            output += i.price
            output += '</br>'
            output += i.description
            output += '</br>'
            output += '</br>'
        return output

class MainView(MethodView):

    def get(self):
        return render_template('main.html')

handler.add_url_rule(
    '/restaurants/<int:restaurant_id>/',
    view_func=RestaurantView.as_view('restaurant_view'))

handler.add_url_rule('/', view_func=MainView.as_view('main_view'))

if __name__ == '__main__':
    app.debug = True
    app.register_blueprint(handler, url_prefix='')
    app.run(host='0.0.0.0', port=5000)
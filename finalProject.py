from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, MenuItem, Restaurant
from flask import session as login_session
import random, string

app = Flask(__name__)
bootstrap = Bootstrap(app)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return "The current session state is %s" % login_session['state']

# Show Restaurants
@app.route('/')
@app.route('/restaurant')
def show_restaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)


# JSON APIs for Restaurant Information
@app.route('/restaurant/JSON')
def show_restaurants_json():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants=[restaurant.serialize for restaurant in restaurants])


@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def show_menu_json(restaurant_id):
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItem=[item.serialize for item in items])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def show_menu_item_json(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_item = session.query(MenuItem).filter_by(id=menu_id, restaurant_id=restaurant_id).one()
    return jsonify(MenuItem=menu_item.serialize)


# Create a Restaurant
@app.route('/restaurant/new', methods=['GET', 'POST'])
def create_restaurant():
    if request.method == 'POST':
        new_restaurant = Restaurant(name=request.form['name'])
        session.add(new_restaurant)
        session.commit()
        return redirect(url_for('show_restaurants'))
    return render_template('newRestaurant.html')


# Edit Restaurant
@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    edited_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edited_restaurant.name = request.form['name']
            session.add(edited_restaurant)
            session.commit()
            return redirect(url_for('show_restaurants'))
    return render_template('editRestaurant.html', restaurant_id=restaurant_id, restaurant=edited_restaurant)


# Delete Restaurant
@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
    deleted_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(deleted_restaurant)
        session.commit()
        return redirect(url_for('show_restaurants', restaurant_id=restaurant_id))
    return render_template('deleteRestaurant.html', restaurant_id=restaurant_id, restaurant=deleted_restaurant)


# Show Menu Items of Restaurant
@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def show_menu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return render_template('menu.html', menuItems=items, restaurant=restaurant)


# Create Menu Item for Restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def create_menu(restaurant_id):
    if request.method == 'POST':
        new_item = MenuItem(name=request.form['name'],
                           description=request.form['description'],
                           price=request.form['price'],
                           course=request.form['course'],
                           restaurant_id=restaurant_id)
        session.add(new_item)
        session.commit()
        return redirect(url_for('show_menu', restaurant_id=restaurant_id))
    return render_template('newMenuItem.html', restaurant_id=restaurant_id)


# Edit Menu Item for Restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
def edit_menu(restaurant_id, menu_id):
    edited_menu = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edited_menu.name = request.form['name']
        if request.form['description']:
            edited_menu.description = request.form['description']
        if request.form['price']:
            edited_menu.price = request.form['price']
        if request.form['course']:
            edited_menu.course = request.form['course']
        session.add(edited_menu)
        session.commit()
        return redirect(url_for('show_menu', restaurant_id=restaurant_id))
    return render_template('editMenuItem.html', restaurant_id=restaurant_id, menu_id=menu_id, menu=edited_menu)


# Delete Menu Item for Restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
def delete_menu(restaurant_id, menu_id):
    deleted_menu = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(deleted_menu)
        session.commit()
        return redirect(url_for('show_menu', restaurant_id=restaurant_id, menu_id=menu_id))
    return render_template('deleteMenuItem.html', restaurant_id=restaurant_id, menu=deleted_menu)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

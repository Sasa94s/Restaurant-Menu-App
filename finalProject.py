from flask import Flask, render_template, url_for, request, redirect, jsonify, make_response, flash
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, MenuItem, Restaurant
from flask import session as login_session
import random, string, httplib2, json, requests

app = Flask(__name__)
bootstrap = Bootstrap(app)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html')


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # if user doesn't exist create a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# User Helper Functions

def create_user(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


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
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new_restaurant = Restaurant(name=request.form['name'], user_id=login_session['user_id'])
        session.add(new_restaurant)
        session.commit()
        return redirect(url_for('show_restaurants'))
    return render_template('newRestaurant.html')


# Edit Restaurant
@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new_item = MenuItem(name=request.form['name'],
                           description=request.form['description'],
                           price=request.form['price'],
                           course=request.form['course'],
                           restaurant_id=restaurant_id,
                           user_id = login_session['user_id'])
        session.add(new_item)
        session.commit()
        return redirect(url_for('show_menu', restaurant_id=restaurant_id))
    return render_template('newMenuItem.html', restaurant_id=restaurant_id)


# Edit Menu Item for Restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
def edit_menu(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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

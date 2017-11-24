from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
@app.route('/restaurants')
def show_restaurants():
    return render_template('index.html')


@app.route('/restaurant/new')
def create_restaurant():
    pass


@app.route('/restaurant/<int:restaurant_id>/edit')
def edit_restaurant(restaurant_id):
    pass


@app.route('/restaurant/<int:restaurant_id>/delete')
def delete_restaurant(restaurant_id):
    pass


@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def show_menu(restaurant_id):
    pass


@app.route('/restaurant/<int:restaurant_id>/menu/new')
def create_menu(restaurant_id):
    pass


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit')
def edit_menu(restaurant_id, menu_id):
    pass

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete')
def delete_menu(restaurant_id, menu_id):
    pass



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

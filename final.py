from flask import Flask, render_template, request, redirect, url_for, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

#Base de datos y session
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
cnnDB = DBSession()

# Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

fakeRests = [{'name': 'The CRUDdy Crab', 'id': '1'}, 
             {'name': 'Blue Burgers', 'id': '2'}, 
             {'name': 'Taco Hut', 'id': '3'}]
# Fake Menu Items
items = [{'name': 'Cheese Pizza', 'description': 'made with fresh cheese', 'price': '$5.99', 'course': 'Entree', 'id': '1'}, 
         {'name': 'Chocolate Cake', 'description': 'made with Dutch Chocolate', 'price': '$3.99', 'course': 'Dessert', 'id': '2'}, 
         {'name': 'Caesar Salad', 'description': 'with fresh organic vegetables', 'price': '$5.99', 'course': 'Entree', 'id': '3'}, 
         {'name': 'Iced Tea', 'description': 'with lemon', 'price': '$.99', 'course': 'Beverage', 'id': '4'}, 
         {'name': 'Spinach Dip', 'description': 'creamy dip with fresh spinach', 'price': '$1.99', 'course': 'Appetizer', 'id': '5'}]
item = {'name': 'Cheese Pizza', 'description': 'made with fresh cheese', 'price': '$5.99', 'course': 'Entree'}

#DataBase connection and session creation would go here



#*************************************************************************
#Implementacion de CRUD para restaurantes
#*************************************************************************
# Task 1: Create route for new Restaurants function here
@app.route('/restaurants/new/', methods=['GET', 'POST'])
def newRestaurant():  
    if request.method == 'POST':
        newRest = Restaurant(name=request.form['txtName'])
        cnnDB.add(newRest)
        cnnDB.commit()
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')

# Task 2: Read route for show all Restaurants function here
@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    recset = cnnDB.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=recset)

# Task 3: Update route for edit Restaurants function here
@app.route('/restaurants/<int:restID>/edit', methods=['GET', 'POST'])
def editRestaurant(restID):
    if request.method == 'POST':
        rest = cnnDB.query(Restaurant).filter_by(id=restID).one()
        rest.name = request.form['txtName']
        cnnDB.add(rest)
        cnnDB.commit()
        return redirect(url_for('showRestaurants'))
    else:
        # rest = next((r for r in fakeRests if r['id'] == str(restID)), None)
        rest = cnnDB.query(Restaurant).filter_by(id=restID).one()
    return render_template('editRestaurant.html', restID=restID, restaurant=rest)

# Task 4: Delete route for delete Restaurants function here
@app.route('/restaurants/<int:restID>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restID):
    if request.method == 'POST':
        rest = cnnDB.query(Restaurant).filter_by(id=restID).one()
        cnnDB.delete(rest)
        cnnDB.commit()
        return redirect(url_for('showRestaurants')) 
    else:
        # rest = next((r for r in fakeRests if r['id'] == str(restID)), None)
        rest = cnnDB.query(Restaurant).filter_by(id=restID).one()
        return render_template('deleteRestaurant.html', restID=restID, restaurant=rest)





#*************************************************************************
#Implementacion de CRUD para platillos por restaurante
#*************************************************************************
# Task 1: Create route for new MenuItem function here
@app.route('/restaurants/<int:restID>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(restID):
    if request.method == 'POST':
        newSaucer = MenuItem(name=request.form['txtName'], restaurant_id=restID, price = request.form['txtCost'], description=request.form['txtDesc'], course=request.form['optCourse'])
        cnnDB.add(newSaucer)
        cnnDB.commit()
        return redirect(url_for('showMenuItems', restID=restID))
    else:
        return render_template('newmenuitem.html', restID=restID)

# Task 2: Read route for show all MenuItems function here
@app.route('/restaurants/<int:restID>/menu/')
def showMenuItems(restID):
    #rest=next((r for r in fakeRests if r['id'] == str(restID)), None)
    rest = cnnDB.query(Restaurant).filter_by(id=restID).one()
    menu = cnnDB.query(MenuItem).filter_by(restaurant_id=restID).all()
    return render_template('menu.html', restID=restID, restaurant=rest, items=menu)

# Task 3: Update route for edit MenuItem function here
@app.route('/restaurants/<int:restID>/menu/<int:menuID>/edit', methods=['GET', 'POST'])  
def editMenuItem(restID, menuID):
    if request.method == 'POST':
        item = cnnDB.query(MenuItem).filter_by(id=menuID).one()
        item.name = request.form['txtName']
        item.price = request.form['txtCost']
        item.description = request.form['txtDesc']
        item.course = request.form['optCourse']
        cnnDB.add(item)
        cnnDB.commit()
        return redirect(url_for('showMenuItems', restID=restID))
    else:
        item = cnnDB.query(MenuItem).filter_by(id=menuID).one()
        return render_template('editMenuItem.html', restID=restID, menuID=menuID, item=item)

# Task 4: Delete route for delete MenuItem function here
@app.route('/restaurants/<int:restID>/menu/<int:menuID>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restID, menuID):
    if request.method == 'POST':
        item = cnnDB.query(MenuItem).filter_by(id=menuID).one()
        cnnDB.delete(item)
        cnnDB.commit()
        return redirect(url_for('showMenuItems', restID=restID))
    else:
        item = cnnDB.query(MenuItem).filter_by(id=menuID).one()
        return render_template('deleteMenuItem.html', restID=restID, menuID=menuID, item=item)    




#*************************************************************************
#Implementacion de Endpoints para API's
#*************************************************************************
@app.route('/restaurants/JSON')
def restaurantsJSON():
    recset = cnnDB.query(Restaurant).all()
    return jsonify(Restaurants=[r.serialize for r in recset])

@app.route('/restaurants/<int:restID>/menu/JSON')
def restaurantMenuJSON(restID):
    menu = cnnDB.query(MenuItem).filter_by(restaurant_id=restID).all()
    return jsonify(MenuItems=[i.serialize for i in menu])

@app.route('/restaurants/<int:restID>/menu/<int:menuID>/JSON')
def menuItemJSON(restID, menuID):
    menu = cnnDB.query(MenuItem).filter_by(id=menuID).one()
    return jsonify(MenuItem=menu.serialize) 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)


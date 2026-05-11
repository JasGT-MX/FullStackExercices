from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants/')
def restaurants():
    restaurants = session.query(Restaurant).all()
    output = ''
    imgMenu = url_for('static', filename='/img/checklist.png')
    for r in restaurants:
        output += '<p> [clave: ' + str(r.id) + ']. ' + r.name
        output += '<a href="/restaurants/' + str(r.id) + '/"><img src="' + imgMenu + '" alt="Ver menu" title="Ver menu" width="32" height="32" style="margin-left: 20px;"></a></p>'
    return output

@app.route('/restaurants/<int:restID>/')
def restaurantMenu(restID):
    #Hacer un select al primer restaurante y su menu
    restaurant = session.query(Restaurant).filter_by(id=restID).one()
    menuItems = session.query(MenuItem).filter_by(restaurant_id=restID)

    #Utilizar template para mostrar el menu del restaurante
    return render_template('menu.html', restaurant=restaurant, items=menuItems)
    # output = '<h1>'+ restaurant.name +'</h1>'
    # for m in menuItems:
    #     output += '<p>   *'+ m.name
    #     output += ' ['+ m.price +']</p>'
    #     output += m.description
    #     output += '</br>'
    # return output


#*************************************************************************
#Implementaciones API EndPoint para regresar datos en JSON
#*************************************************************************
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=menuItem.serialize)


#*************************************************************************
#Implementacion de CRUD para restaurantes
#*************************************************************************
# Task 1: Create route for newMenuItem function here
@app.route('/restaurants/<int:restID>/new/', methods=['GET', 'POST'])
def newMenuItem(restID):
    #Hace el guardado del nuevo item en la base de datos
    if request.method == 'POST':
        newItem = MenuItem(
            name=request.form['txtName'], restaurant_id=restID)
        session.add(newItem)
        session.commit()
        flash('El nuevo platillo ha sido agregado al menú!')
        return redirect(url_for('restaurantMenu', restID=restID))
    #Muestra el formulario para crear un nuevo item
    else:
        return render_template('newmenuitem.html', restaurant_id=restID)


# Task 2: Create route for editMenuItem function here
@app.route('/restaurants/<int:restID>/<int:menuID>/edit', methods=['GET', 'POST'])
def editMenuItem(restID, menuID):
    editItem = session.query(MenuItem).filter_by(id=menuID).one()
    #Hace el guardado de las actualizaciones del item en la base de datos
    if request.method == 'POST':
        if request.form['txtName']:
            editItem.name = request.form['txtName']
        session.add(editItem)
        session.commit()
        flash('El nombre del platillo se actualizo!')
        return redirect(url_for('restaurantMenu', restID=restID))
    #Muestra el formulario para crear un nuevo item
    else:
        return render_template('editmenuitem.html', restaurant_id=restID, menu_id=menuID, item=editItem)

# Task 3: Create a route for deleteMenuItem function here
@app.route('/restaurants/<int:restID>/<int:menuID>/del', methods=['GET', 'POST'])
def deleteMenuItem(restID, menuID):
    delItem = session.query(MenuItem).filter_by(id=menuID).one()
    #Hace el borrado del item en la base de datos
    if request.method == 'POST':
        session.delete(delItem)
        session.commit()
        flash('El platillo se elimino del menú!')
        return redirect(url_for('restaurantMenu', restID=restID))
    #Muestra el formulario para crear un nuevo item
    else:
        return render_template('deletemenuitem.html', restaurant_id=restID, menu_id=menuID, item=delItem)



if __name__ == '__main__':
    #app.run(debug=True) 
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
    
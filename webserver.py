import os
import sys


from sqlalchemy import create_engine, null
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, MenuItem, Base
from http.server import BaseHTTPRequestHandler, HTTPServer
import email   #Reemplaza a cgi para manejar los datos del formulario


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            #Evita generar error al buscar favicon.ico o archivos de seguridad
            if self.path == "/favicon.ico" or ".well-known" in self.path:
                self.send_response(404)
                self.end_headers()
                return
            
             # Lógica para servir imágenes
            if self.path.startswith("/images/"):
                try:
                    # Construye la ruta real (ej: ./images/edit.png)
                    # self.path[1:] elimina la primera barra '/'
                    file_path = os.path.join(os.getcwd(), self.path[1:])
                    
                    with open(file_path, 'rb') as file:
                        self.send_response(200)
                        self.send_header('Content-type', 'image/png')
                        self.end_headers()
                        self.wfile.write(file.read())
                    return
                except IOError:
                    self.send_error(404, 'Imagen no encontrada')
                    return
    
            # ********* CRUD RESTAURANTES ********* 
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            if self.path.endswith("/hello") or self.path.endswith("/hola"):
                msg = "Hello!" if self.path.endswith("/hello") else "Hola!"

                self.wfile.write(getHTML(msg, "hi").encode('utf-8'))
                print ("GET request for {self.path} received".format(self=self))
                return 
            elif self.path.endswith("/restaurants"):
                cnnDB = configDB()
                recSet = cnnDB.query(Restaurant).all()
                
                print("---> Totales de registros: " + str(len(recSet)))

                self.wfile.write(getHTML(recSet, "read").encode('utf-8'))
                print ("GET request for {self.path} received - Status 200".format(self=self))
                return
            elif self.path.endswith("/new"):
                self.wfile.write(getHTML(None, "create").encode('utf-8'))
            elif self.path.endswith("/edit"):
                restaurant_id = self.path.split("/")[2]
                cnnDB = configDB()
                restaurant = cnnDB.query(Restaurant).filter_by(id=restaurant_id).one()
                if restaurant:
                    self.wfile.write(getHTML(restaurant, "update").encode('utf-8'))
                else:
                    self.send_error(404, 'Restaurant no encontrado: %s' % self.path)
            elif self.path.endswith("/delete"):
                restaurant_id = self.path.split("/")[2]
                cnnDB = configDB()
                restaurant = cnnDB.query(Restaurant).filter_by(id=restaurant_id).one()
                if restaurant:
                    self.wfile.write(getHTML(restaurant, "delete").encode('utf-8')) 
                else:
                    self.send_error(404, 'Restaurant no encontrado: %s' % self.path)                    
            else:
                self.send_error(404, 'Pagina no encontrada: %s' % self.path)
        except IOError:
            self.send_error(404, 'Error al ingresar a la pagina: %s' % self.path)



    def do_POST(self):
        try:
            # 1. Preparar lectura de datos
            conType = self.headers.get('Content-Type')
            content_length = int(self.headers.get('Content-Length'))
            body = self.rfile.read(content_length)
            
            # Función auxiliar para extraer valores del formulario
            def get_val(field, body):
                parts = body.split(b'\r\n')
                for i, p in enumerate(parts):
                    if f'name="{field}"'.encode() in p:
                        return parts[i + 2].decode('utf-8').strip()
                return None

            print("----------------------------------" + self.path)
           
            # Caso: CREATE Restaurante
            if self.path.endswith("/create"):
                new_name = get_val("txtName", body)
                if new_name:
                    cnn = configDB()
                    cnn.add(Restaurant(name=new_name))
                    cnn.commit()
                # Redirigir para ver el resultado
                self.send_response(303)
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return
            # Caso: EDITAR Restaurante
            elif self.path.endswith("/edit"):
                restaurant_id = self.path.split("/")[2]
                new_name = get_val("txtNewName", body)
                cnn = configDB()
                restaurant = cnn.query(Restaurant).filter_by(id=restaurant_id).one()
                if restaurant and new_name:
                    restaurant.name = new_name
                    cnn.commit()
                self.send_response(303)
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return
            # Caso: BORRAR Restaurante
            elif self.path.endswith("/del"):
                restaurant_id = self.path.split("/")[2]
                cnn = configDB()
                restaurant = cnn.query(Restaurant).filter_by(id=restaurant_id).one()
                if restaurant:
                    cnn.delete(restaurant)
                    cnn.commit()
                self.send_response(303)
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return
            # --- LÓGICA ORIGINAL (FORMULARIO "HELLO") ---
            else:
            # Si no es una ruta de BD, ejecutamos tu código original de respuesta
                respContent = get_val("message", body) or ""

                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                output = f"""
                    <html><body>
                        <h2>Okay, how about this:</h2>
                        <h1>{respContent}</h1>
                        <form method='POST' enctype='multipart/form-data' action='/hello'>
                            <h2>What would you like me to say?</h2>
                            <input name="message" type="text">
                            <input type="submit" value="Submit">
                        </form>
                        <br><a href='/restaurants'>Ir al listado de restaurantes</a>
                    </body></html>
                    """
                self.wfile.write(output.encode('utf-8'))
                print(f"POST request for {self.path} processed")

        except Exception as e:
            print(f"Error: {e}")
            self.send_error(500)



def configDB():
    # Configuración de la base de datos
    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def getHTML(rows, htmlType):
    
    htmlResp = ""
    cnt = 0
    if (htmlType == "hi"):
        htmlResp = f"""
                <html><body>
                    <h1>{rows}</h1>
                    <form method='POST' enctype='multipart/form-data' action='/hello'>
                        <h2>What would you like me to say?</h2>
                        <input name="message" type="text">
                        <input type="submit" value="Submit">
                    </form>
                </body></html>
                """
    elif (htmlType == "create"):
        htmlResp = f"""<html><body>
                    <h1>Agregar un nuevo restaurant</h1>
                    <form method='POST' enctype='multipart/form-data' action='/create'>
                        <h2>Nuevo restaurant:</h2>
                        <input name="txtName" type="text" placeholder="Ingrese el nombre del restaurant">
                        <input type="submit" value="Crear">
                    </form>
                </body></html>
                """
    elif (htmlType == "read"):
        if (len(rows) == 0):
            return f"<html><body><h1>No hay restaurantes registrados</h1><a href='/new'>Nuevo restaurant</a></body></html>"
        
        htmlResp = f"""<html><body>
                    <h1>Restaurants</h1>
                    """           
        for r in rows:
            cnt += 1
            htmlResp += f"<p>{cnt}. {r.name}   "
            htmlResp += f"<a href='/restaurant/{r.id}/edit'><img src='/images/edit.png' alt='Edit name' width='32' height='32' style='margin-left: 20px;'></a>"
            htmlResp += f"<a href='/restaurant/{r.id}/delete'><img src='/images/trash.png' alt='Delete restaurant' width='32' height='32' style='margin-left: 20px;'></a><br>"
            htmlResp += f"</p>"

        htmlResp += f""" ________________________________________________________________________________________________________<br>
                <h2><a href='/new'>Nuevo restaurant</a></h2>
            </body></html>
            """
    elif (htmlType == "update"):
        htmlResp = "<html><body><h1>"
        htmlResp += rows.name 
        htmlResp += "</h1>"
        htmlResp += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % rows.id
        htmlResp += "<input name='txtNewName' type='text' placeholder='%s'>" % rows.name
        htmlResp += "<input type='submit' value='Renombrar'></form></body></html>"  
    elif (htmlType == "delete"):
        htmlResp = "<html><body><h1 style='display: inline'>Seguro que desea eliminar el restaurant: <p style='color: firebrick; font-weight: bold; display: inline; font-style: italic;'>%s</p>?</h1>" %rows.name
        htmlResp += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/del'>" % rows.id
        htmlResp += "<input name='btnDel' type='submit' value='Eliminar'></form></body></html>"

    return htmlResp


def main():
    try:
        port = 8088
        server = HTTPServer(('', port), WebServerHandler)
        print ("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print (" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()

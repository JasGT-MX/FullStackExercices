from http.server import BaseHTTPRequestHandler, HTTPServer
import email   #Reemplaza a cgi para manejar los datos del formulario


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path == "/favicon.ico" or ".well-known" in self.path:
                self.send_response(404)
                self.end_headers()
                return
    
            if self.path.endswith("/hello") or self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                msg = "Hello!" if self.path.endswith("/hello") else "Hola!"

                output = f"""
                <html><body>
                    <h1>{msg}</h1>
                    <form method='POST' enctype='multipart/form-data' action='/hello'>
                        <h2>What would you like me to say?</h2>
                        <input name="message" type="text">
                        <input type="submit" value="Submit">
                    </form>
                </body></html>
                """
                self.wfile.write(output.encode('utf-8'))
                print ("GET request for {self.path} received".format(self=self))
                return       
            else:
                self.send_error(404, 'Pagina no encontrada: %s' % self.path)
        except IOError:
            self.send_error(404, 'Error al ingresar a la pagina: %s' % self.path)

    def do_POST(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            # Leer el encabezado de tipo de contenido
            conType = self.headers.get('Content-Type')
            
            # En Python 3, usamos email.message para parsear formularios multipart
            msg = email.message_from_string(f"Content-Type: {conType}\n\n")
            boundary = msg.get_param('boundary').encode('utf-8')
            
            # Leer el cuerpo de la petición
            content_length = int(self.headers.get('Content-Length'))
            body = self.rfile.read(content_length)
            
            # Buscamos el contenido entre los boundaries del formulario
            parts = body.split(boundary)
            respContent = ""
            for p in parts:
                if b'name="message"' in p:
                    # Separar encabezados de la parte del contenido real
                    respContent = p.split(b'\r\n\r\n')[1].split(b'\r\n')[0].decode('utf-8')

            output = f"""
                <html><body>
                    <h2>Okay, how about this:</h2>
                    <h1>{respContent}</h1>
                    <form method='POST' enctype='multipart/form-data' action='/hello'>
                        <h2>What would you like me to say?</h2>
                        <input name="message" type="text">
                        <input type="submit" value="Submit">
                    </form>
                </body></html>
                """
            self.wfile.write(output.encode('utf-8'))
            print ("POST request for {self.path} received".format(self=self))
        except:
            pass

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

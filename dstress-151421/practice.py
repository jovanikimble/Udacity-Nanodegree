import sys
import os
import jinja2
import socket as sock

template_dir = os.path.join(os.getcwd(), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Packet(object):

  def __init__(self):
    self.content = ''

  def write(self, s):
    self.content = self.content + s

class Response(object):

  def __init__(self):
    self.out = Packet()

class Webapp2Handler(object):

  def __init__(self):
    self.response = Response()

class MainHandler(Webapp2Handler):

  def get(self):
   # with open(template_dir + '/home.html') as f:
   #   file_content = f.read()
   #final_content = file_content.format(name = 'Jovani', last = 'Kimble')
   t = jinja_env.get_template('home.html')
   final_content = t.render(name='Jovani', last='Kimble', n=5,
    foods=["Mexican", "Soul", "Thai"], state = 'tired')
   self.response.out.write(final_content)

  def post(self):

    self.response.out.write("Main Handler post method")

class NewpostHandler(Webapp2Handler):

  def get(self):
    self.response.out.write('This is the newpost page')

  def post(self):

    self.response.out.write("Newpost Handler post method")

HOST = 'localhost'
PORT = 10036
ADDR = (HOST, PORT)
BUFSIZE = 4096

class WSGIApplication(object):

  def __init__(self, handler_configs):

    self.handlerMap = {}
    for handler_config in handler_configs:
      path = handler_config[0]
      class_name = handler_config[1]
      self.handlerMap[path] = class_name

    self._create_socket()

  def _create_socket(self):
    self.server_socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    self.server_socket.bind((ADDR))
    self.server_socket.listen(1)
    print('Listening on port {0}'.format(PORT))

  def _send_packet(self, conn, packet):
    conn.send(packet.content)

  def _send(self, conn, msg):
    packet = Packet()
    packet.write(msg)
    self._send_packet(conn, packet)

  def run(self):

    while True:
      conn, addr = self.server_socket.accept()
      message = conn.recv(4096)
      print message
      if not message:
        break

      # Parse the message
      parts = message.split(' ')
      if len(parts) != 2:
        self._send(conn,'Message must contain two parts')
        continue

      verb = parts[0]
      path = parts[1]

      class_name = self.handlerMap.get(path)
      if class_name is None:
        self._send(conn, 'Unrecognized Path')
      else:
        handler = class_name()
        if verb == 'GET':
          handler.get()
        elif verb == 'POST':
          handler.post()

        self._send_packet(conn, handler.response.out)
        conn.close()

    conn.close()

def main():
  handlers = [
    ('/', MainHandler),
    ('/newpost', NewpostHandler)
  ]
  app = WSGIApplication(handlers)
  try:
    app.run()
  except Exception as e:
    print(e)

main()
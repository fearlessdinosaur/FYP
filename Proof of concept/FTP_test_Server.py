# code taken from https://www.techinfected.net/2017/07/create-simple-ftp-server-client-in-python.html
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer()
authorizer.add_user("user", "12345", "Files", perm="elradfmw")
authorizer.add_anonymous("Files", perm="elradfmw")

handler = FTPHandler
handler.authorizer = authorizer

server = FTPServer(("127.0.0.1", 1026), handler)
server.serve_forever()
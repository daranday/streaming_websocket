import sys
import gflags
from websocket_server import WebsocketServer

gflags.DEFINE_integer('port', 9001, 'port')
gflags.DEFINE_string('host', '0.0.0.0', 'hostname')
FLAGS = gflags.FLAGS


def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])


# Called for every client disconnecting
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])


# Called when a client sends a message
def message_received(client, server, message):
    server.send_message(client, message)


if __name__ == '__main__':
    FLAGS(sys.argv)
    server = WebsocketServer(FLAGS.port, host=FLAGS.host)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()

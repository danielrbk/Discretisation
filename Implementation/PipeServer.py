import socket
import _thread

from Implementation.Constants import MAX_MSG_SIZE
host_name = socket.gethostname()
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((host_name, 7070))
serversocket.listen(5)


def run_client(clientsocket, address):
    init_msg = clientsocket.recv(MAX_MSG_SIZE).decode("utf-8")
    msg = ""
    while len(init_msg) != 0:
        msg += init_msg
        init_msg = clientsocket.recv(MAX_MSG_SIZE).decode("utf-8")
        print(msg)
    clientsocket.close()
    msg = msg.replace("<EOF>","")
    print(msg)

if __name__=="__main__":
    while True:
        # accept connections from outside
        (clientsocket, address) = serversocket.accept()
        if address[0] != host_name:
            clientsocket.close()
        # now do something with the clientsocket
        # in this case, we'll pretend this is a threaded server
        _thread.start_new_thread(run_client,(clientsocket,address))
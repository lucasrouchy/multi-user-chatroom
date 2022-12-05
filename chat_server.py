import sys
import socket
import select
import queue
import json
def run_server(port):
    
    s = socket.socket()
    # s.setblocking(0)
    s.bind(('', port))
    s.listen()
    inputs = [s]
    outputs = []
    buffer = {}

    while True:
        r, _, _ = select.select(inputs, outputs, inputs)
        for server in r:
            if server is s:
                # if the new socket is the listener socket accept the connection
                new_socket, _ = server.accept()
                print(new_socket.getpeername(), ':  connected')
                inputs.append(new_socket)
                
            else:
                
                data = server.recv(4096)
                
                if len(data) != 0:
                    de_data = data.decode()
                    data_managing(server, de_data, buffer)
    
                else:
                    server.close()
                    inputs.remove(server)
                    name = buffer.pop(server)
                    data_sending(make_leave_packet(name), buffer)
                    print('*** {name} has left the chat'.format(name=name))

def make_leave_packet(name):
    return json.dumps({"type": "leave", "nickname": name})

def make_join_packet(name):
    return json.dumps({"type": "join", "nickname": name})

def make_client_packet(data, buffer):
    return json.dumps({"type": "chat", "message": data, "nickname": buffer})
# data managing function extracts the repeated code I had that would manage the data.
# this function works by taking that data and making it a packet or JSON payload and depending on what type of packet it is it will either go into the hello or chat payload conditionals. 
def data_managing(s, data, buffer):
    p = json.loads(data)

    if p['type'] == 'hello':
        print('***' + ' {name}  has joined the chat'.format(name = p['nickname']))
        buffer[s] = p['nickname']
        data_sending(make_join_packet(p['nickname']), buffer)
    
    elif p['type'] == 'chat':
        print('{client_name}: {message}'.format(client_name= buffer[s], message= p['message']))
        data_sending(make_client_packet(p['message'], buffer[s]), buffer)
    
# data sending function extracts the try and except clause from my previous implementation.
# basically just takes the JSON payload(data) and tries to send it to the client desired.
# if the data is not sent there is an expecption which will let the chat room know there was a message failure
def data_sending(data, buffer):
    # print(data)
    for cs in buffer:
        try:
            cs.send(data.encode())
                           
        except:
            print('Message failure to {client}'.format(client= cs))
            print('/n next client')

def usage():
    print("usage: select_server.py port", file=sys.stderr)    

def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1
    run_server(port)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

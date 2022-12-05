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
    
    client_names = {}
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
                    data_managing(server, de_data, client_names)
                    
                    
            
                else:
                    server.close()
                    inputs.remove(server)
                    name = client_names.pop(server)
                    data_sending(make_leave_packet(name), client_names)
                    print('*** {name} has left the chat'.format(name=name))
def make_leave_packet(name):
    return json.dumps({"type": "leave", "nickname": name})

def make_join_packet(name):
    return json.dumps({"type": "join", "nickname": name})

def make_client_packet(data, client_names):
    return json.dumps({"type": "chat", "message": data, "nickname": client_names})

def data_managing(s, data, client_names):
    p = json.loads(data)
    if p['type'] == 'hello':
        print('***' + ' {name}  has joined the chat'.format(name = p['nickname']))
        client_names[s] = p['nickname']
        data_sending(make_join_packet(p['nickname']), client_names)
    elif p['type'] == 'chat':
        print('{client_name}: {message}'.format(client_name= client_names[s], message= p['message']))
        data_sending(make_client_packet(p['message'], client_names[s]), client_names)
        
def data_sending(data, client_names):
    print(data)
    for cs in client_names:
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

import sys
import socket
import select
import queue
import json
def run_server(port):
    
    s = socket.socket()
    s.setblocking(0)
    s.bind(('', port))
    s.listen()
    inputs = [s]
    outputs = []
    message_queue = {}
    client_names = {}
    while True:
        r, _, _ = select.select(inputs, outputs, inputs)
        for server in r:
            if server is s:
                # if the new socket is the listener socket accept the connection
                new_socket, _ = server.accept()
                print(new_socket.getpeername(), ':  connected')
                new_socket.setblocking(0)
                inputs.append(new_socket)
                message_queue[new_socket] = queue.Queue()
            else:
                
                data = server.recv(4096)
                
                if len(data) != 0:
                    p = json.loads(data.decode())
                    
                    if p['type'] == 'hello':
                        print('{name}    has joined chat'.format(name = p['john']))
                        client_names[server] = p['john']
                        print(make_join_packet(p['john']))
                        
                        for client_s in client_names:
                            
                            try:
                                client_s.send(make_join_packet(p['john']).encode())
                           
                            except:
                                print('Message failure for client socket {client}'.format(client= client_s))
                                print('/n next client')
                    
                    elif p['type'] == 'chat':
                        print('{client_name}: {message}'.format(client_name= client_names[server], message= p['message']))
                        print(data.decode())
                        for client_s in client_names:
                            try:
                                client_s.send(make_client_packet(p['message']).encode())
                            except:
                                print('Message failure for client socket {client}'.format(client= client_s))
                                print('/n next client')
            
                else:
                    server.close()
                    inputs.remove(server)
                    client_name = client_names.pop(server)
                    print(make_leave_packet(client_name))
                    for client_s in client_names:
                        try:
                            client_s.send(make_leave_packet(client_name).encode())
                           
                        except:
                            print('Message failure for client socket {client}'.format(client= client_s))
                            print('/n next client')
                    print('{name} has left'.format(name = client_name))

def make_leave_packet(name):
    return json.dumps({"type": "leave", "john": name})

def make_join_packet(name):
    return json.dumps({"type": "join", "john": name})

def make_client_packet(data, client_names):
    return json.dumps({"type": "chat", "message": data, "john": client_names})

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

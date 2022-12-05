import sys
import socket
import time
import threading
import json

from chatui import *


def usage():
    print("usage: select_client.py prefix host port", file=sys.stderr)
def main(argv):
    try:
        name = argv[1]
        host = argv[2]
        port = int(argv[3])
    except:
        usage()
        return 1

    # Make the client socket and connect
    s = socket.socket()
    s.connect((host, port))
    s.send(make_intro_packet(name).encode())

    init_windows()

    t_server = threading.Thread(target=server_messages, args=(s,), daemon=True)
    t_client = threading.Thread(target=client_messages, args=(s, name))
    threads = [t_server, t_client]
    for t in threads:
        t.start()
    threads[1].join()
    end_windows()

    return 0
    
    

def client_messages(s, name):
    while True:
        data = read_command(name + '> ')
        
        if data[0] == '/':
            if data == '/q':
                s.close()
                return
            else:
                print_message('Command not recognized')
        elif len(data) != 0:
            s.send(make_chat_packet(data).encode())
        else:
            continue

def server_messages(s):
    while True:
        data = s.recv(4096).decode()
        data = json.loads(data)
        print_message(make_message(data))

def make_message(packet):
    if packet['type'] == 'chat':
        return '***' + packet['nickname'] + ': ' + packet['message']
    elif packet['type'] == 'leave':
        return '***' + packet['nickname'] + ' has left'
    elif packet['type'] == 'join':
        return '***' + packet['nickname'] + ' has joined'    

def make_intro_packet(name):
    return json.dumps({'nickname': name, 'type': 'hello'})

def make_chat_packet(data):
    return json.dumps({'message': data, 'type': 'chat'})

if __name__ == "__main__":
    sys.exit(main(sys.argv))
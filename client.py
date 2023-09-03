import socket
import threading
import jwt
import random
import pickle
import pymongo
import requests
import werkzeug.security as ws
from utils import *
import ast
from functools import wraps
from flask import request,jsonify
import datetime
host = "127.0.0.1"
port = 5555
current_user = ""
current_user_own_port = 0
n = 1
already_printed_users = []

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["usersDB"]
users_schema = mydb["users"]

messagesdb = myclient["messagesDB"]
messages_schema = messagesdb["messages"]

authenticated = False
status=""

connect_with_peer = False
SECRET_KEY = "SECRET_KEY"

def token_checker(token):
 
       if not token:
           print('a valid token is missing')
           return False
       try:
           data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
           all_users = requests.get("http://127.0.0.1:5000/client").json()
           current_user = ""
           for user in all_users:
               if user['username']==data['username']:
                    current_user = user
                    break

       except:
           print('token is invalid')
           return False
       print('token is valid')
       return True

while not authenticated:
    all_users = requests.get("http://127.0.0.1:5000/client").json()

    prompt = input("Login or Signup?")

    if prompt.lower() == "signup":
        username = input("Your username: ")
        for i in all_users:
            if username == i["username"]:
                print("This user already exists!")
                continue

        password = input("Your password: ")
        confirmation_password = input("Your confirmation password: ")
        if password == confirmation_password:
            personal_port = random.randint(40000, 60000)
            status="offine"
            requests.post(f"http://127.0.0.1:5000/client/{username}/{password}/{personal_port}/{status}")
            continue
        else:
            print("Confirmation password does not match, try again!")
            continue

    elif prompt.lower() == "login":
        username = input("Your username: ")
        password = input("Your password: ")
        match = False
        success = False
        for name in all_users:
            if username == name["username"]:
                match = True
                break
        if match:
            for user in all_users:
                if user["username"] == username and user["password"] == password:
                    token = jwt.encode({"username": user["username"], "password": user["password"], "personal_port": user["personal_port"], "status": user["status"]}, SECRET_KEY, "HS256") 
                    token_check = token_checker(token=token)
                    if token_check == False:
                        print('token check didnt pass\ncannot confirm authentication.')
                        break

                    success = True
                    status="online"
                    current_user = username
                    current_user_own_port = user["personal_port"]
                    requests.put(f"http://127.0.0.1:5000/client/{username}/{password}/{current_user_own_port}/{status}")
                    authenticated = True


            if not success:
                print("Incorrect username or password. Please try again!")

        else:
            print("This user does not exist!")
            continue

def listen(s, host, port):
    while True:
        msg, addr = s.recvfrom(UDP_MAX_SIZE)
        msg_port = addr[1]
        if msg_port != port:
            payload = pickle.loads(msg).get_payload()
            username = pickle.loads(msg).get_username()
            hashed_message = pickle.loads(msg).get_hashed_message()

            if not ws.check_password_hash(hashed_message, payload):
                print(f'{username} tried to spoof you\nconnection closed!')
                break


        allowed_ports = threading.current_thread().allowed_ports
        if msg_port not in allowed_ports:
            continue
        if not msg:
            continue


        msg = pickle.loads(msg)


        if not ws.check_password_hash(msg.get_hashed_message(), msg.get_payload()):
            print(f'{msg.get_username()} tried to spoof you\nconnection closed!')
            break

        if '__' in msg.get_payload():
            content = msg.get_payload().split('__')
            if content[0] == 'show_clients':
                if content[1] == '[]':
                    print("There is not any other active client yet!")
                else:
                    print("Active clients are: \n")
                    for member in ast.literal_eval(content[1]):
                        if member in already_printed_users:
                            continue
                        else:
                            global n
                            print('\r\r' + f'{n}) username: {member["username"]}' + f' personal_port: {member["personal_port"]} status: {member["status"]}')
                            already_printed_users.append(member["username"])
                            n += 1
            n=1

        else:
            global connect_with_peer
            connect_with_peer = True
            peer_name = f'{username}'
            print('\r\r' + f'{peer_name}: ' + payload + '\n' + f'>>> ', end='')


def listen_thr(target, socket, host, port):
    th = threading.Thread(target=target, args=(socket, host, port), daemon=True)
    th.start()
    return th

# @token_required
def connect(host, port, personal_port):
    print('Welcome to chat!\nTo see the command type help: in a chat.')
    own_port = int(personal_port)
    print(f'Your personal port is: {own_port}')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    s.bind((host, own_port))
    listen_thread = listen_thr(listen, s, host, port)
    allowed_ports = [port]
    listen_thread.allowed_ports = allowed_ports
    sendto = (host, port)
    s.sendto(pickle.dumps(Message(payload='__join', username=current_user, client_id=f"{personal_port}",
                                  hashed_message=ws.generate_password_hash('__join', 'md5'))), sendto)
    connect_with = False

    while True:
        try:
            global connect_with_peer
            if connect_with == True:
                all_messages = requests.get("http://127.0.0.1:5000/message").json()
                for i in all_messages:
                    if i["to_username"] == username and connect_with_peer==False:
                        # print(connect_with_peer)
                        print(i["from_username"],":",i["msg"])
                        requests.delete(f"http://127.0.0.1:5000/message/{i['from_username']}/{username}/{i['msg']}")
                    if i["to_username"] == username and connect_with_peer==True:
                        requests.delete(f"http://127.0.0.1:5000/message/{i['from_username']}/{username}/{i['msg']}")
            msg = input(f'>>> ')
            command = msg.split(' ')[0]
            if command in COMMANDS:

                if msg.startswith('disconnect:'):
                    peer_port = sendto[-1]
                    allowed_ports.remove(peer_port)
                    sendto = (host, port)
                    print(f'Successfully disconnected!')
                    connect_with = False
                    
                    connect_with_peer = False
                    continue
                if msg == 'end_session:':
                    peer_port = sendto[-1]
                    allowed_ports.remove(peer_port)
                    sendto = (host, port)
                    print(f'Disconnect from client{peer_port}')
                    connect_with = False
                    print(f'you successfully disconnected from the chat!')
                    s.sendto(pickle.dumps(Message(username="", payload='end_session:', client_id=f"{own_port}",
                                                hashed_message=ws.generate_password_hash('end_session:', 'md5'))), sendto)
                    quit()
                if msg.startswith('connect:'):
                    connect_with = True
                    peername = msg.split(' ')[-1]
                    all_users = requests.get("http://127.0.0.1:5000/client").json()
                    peer=0
                    falserequest = True
                    for user in all_users:
                        if user['username'] == peername:
                            peer = user['personal_port']
                            falserequest=False
                    if falserequest == True:
                        print("such user doesnt exist")
                        continue
                    # print(msg)
                    peer_port = int(peer) # peer_port = int(peer.replace('client', ''))
                    allowed_ports.append(peer_port)
                    sendto = (host, peer_port)
                    print(f'Connect to {peername}')
                if msg == 'help:':
                    print(HELP_TEXT)
            else:
                if connect_with == True:
                    from_username = username
                    to_username=""
                    all_users = requests.get("http://127.0.0.1:5000/client").json()
                    for user in all_users:
                        if int(user["personal_port"]) == sendto[1] and connect_with_peer==False:
                            to_username = user["username"]
                            requests.post(f"http://127.0.0.1:5000/message/{from_username}/{to_username}/{msg}")
                    s.sendto(pickle.dumps((Message(username=username, payload=msg, client_id=f"{own_port}",
                                                hashed_message=ws.generate_password_hash(msg, 'md5')))), sendto)
        except:
            peer_port = sendto[-1]
            allowed_ports.remove(peer_port)
            sendto = (host, port)
            print(f'Disconnect from client{peer_port}')
            connect_with = False
            print(f'you successfully disconnected from the chat!')
            s.sendto(pickle.dumps(Message(username="", payload='end_session:', client_id=f"{own_port}",
                                                hashed_message=ws.generate_password_hash('end_session:', 'md5'))), sendto)
            status="offline"
            requests.put(f"http://127.0.0.1:5000/client/{username}/{password}/{current_user_own_port}/{status}")
            quit()
if __name__ == '__main__':
    connect(host, port, current_user_own_port)
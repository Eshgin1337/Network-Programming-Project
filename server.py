import pickle
import requests
import sqlite3
import socket
import pymongo
import sys
import werkzeug.security as ws
from utils import *

host = "127.0.0.1"
port = 5555

localhost = 'http://127.0.0.1:5000'
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["usersDB"]
users_schema = mydb["users"]

current_active_members = []


# addresses = []

def listen(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    s.bind((host, port))
    print(f'Listening at {host}:{port}')

    while True:
        msg, addr = s.recvfrom(UDP_MAX_SIZE)
        if not msg:
            continue
        payload = pickle.loads(msg).get_payload()
        username = pickle.loads(msg).get_username()
        hashed_message = pickle.loads(msg).get_hashed_message()
        client_id1 = pickle.loads(msg).get_client_id()
        if not ws.check_password_hash(hashed_message, payload):
            print(f'{username} tried to spoof you\nconnection closed!')
            break

        if payload == '__join':
            
            if addr not in current_active_members:
                current_active_members.append(addr)
            # all_members = requests.get("http://127.0.0.1:5000/client").json()


            # active_users_for_current_user = []
            # for address in current_active_members:
            #     active_members = []
            #     for user in all_members:
                    
            #         # print(user)
            #         # print(user["personal_port"],address[1],address,addr)
            #         if int(user["personal_port"])!=int(address[1]):
            #             active_members.append({"username": user["username"], "personal_port": user["personal_port"],"status": user["status"]})
            #             print(active_members)
            #         if int(user["personal_port"]) != int(address[1]) and address == addr:
            #             active_users_for_current_user.append({"username": user["username"], "personal_port": user["personal_port"], "status": user["status"]})

            #     members_msg1 = active_users_for_current_user
            #     members_msg = active_members
            #     # print(address)
            #     # print(members_msg,members_msg1)
            #     if address != addr:
            #         s.sendto(pickle.dumps(Message(payload=f'show_clients__{members_msg}', username="server",
            #                                       hashed_message=ws.generate_password_hash(
            #                                           f'show_clients__{members_msg}', 'md5'))), address)
            #     if address == addr:
            #         s.sendto(pickle.dumps(Message(payload=f'show_clients__{members_msg1}', username="server",
            #                                       hashed_message=ws.generate_password_hash(
            #                                           f'show_clients__{members_msg1}', 'md5'))), address)
        print(f'{username} has joined chat')


if __name__ == '__main__':
    listen(host, port)

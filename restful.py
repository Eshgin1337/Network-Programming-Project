import json

from flask import Flask
from flask_restful import Resource, reqparse, Api
import pymongo
app = Flask('__name__')

api = Api(app=app)
parser = reqparse.RequestParser()

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["usersDB"]
users_schema = mydb["users"]

messagesdb = myclient["messagesDB"]
messages_schema = messagesdb["messages"]

class UserApi(Resource):
    def get(self, username="", password="", personal_port="",status=""):
        all_users = []
        users = []
        for i in users_schema.find():
            all_users.append(i)
        for i in all_users:
            # print(i)
            users.append({"username": i["username"], "password": i["password"], "personal_port": i["personal_port"], "status": i["status"]})
        return users

    def post(self, username, password, personal_port,status):
        users_schema.insert_one({"username": username, "password": password, "personal_port": personal_port,"status": status})
        
    def put(self, username, password, personal_port,status):
        if str(status)=="offline":
            print('yes')
            users_schema.update_one({"username": username, "password": password, "personal_port": personal_port},{ "$set" :{"status": "offline"}})
            return 1
        if str(status)=="online":
            print('no')
            users_schema.update_one({"username": username, "password": password, "personal_port": personal_port},{ "$set" :{"status": "online"}})
            return 0

class MessageApi(Resource):
    def get(self,from_username="",to_username="",msg=""):
        all_messages = []
        messages = []
        for i in messages_schema.find():
            all_messages.append(i)
        for i in all_messages:
            messages.append({"from_username" : i["from_username"],"to_username" : i["to_username"], "msg": i["msg"]})
        return messages
    def post(self,from_username,to_username,msg):
        messages_schema.insert_one({"from_username" : from_username,"to_username" : to_username, "msg": msg})
    def delete(self,from_username,to_username,msg):
        messages_schema.delete_one({"from_username" : from_username,"to_username" : to_username, "msg": msg})

api.add_resource(UserApi, '/client','/client/<string:username>/<string:password>/<string:personal_port>/<string:status>')

api.add_resource(MessageApi, '/message','/message/<string:from_username>/<string:to_username>/<string:msg>')

if __name__ == "__main__":
    app.run(debug=True)


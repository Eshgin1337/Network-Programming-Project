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



class MyApi(Resource):
    def get(self, username="", password="", personal_port=""):
        all_users = []
        users = []
        for i in users_schema.find():
            all_users.append(i)
        for i in all_users:
            # print(i)
            users.append({"username": i["username"], "password": i["password"], "personal_port": i["personal_port"]})
        return users

    def post(self, username, password, personal_port):
        users_schema.insert_one({"username": username, "password": password, "personal_port": personal_port})
        
    # def put(self,client_id,username):
    #     conn1 = sqlite3.connect('database.db')
    #     cur1=conn1.cursor()
    #     users1 = cur1.execute('SELECT * FROM USER;')
    #     for i in users1:
    #         if i[0]==client_id:
    #             cur1.execute(f"""UPDATE USER
    #             SET username="{username}"
    #             where client_id="{client_id}";
    #             """)
    #             conn1.commit()
    #             return "successfully updated username"
    #     abort(404,message="No such client id exists")
        

    # def delete(self,personal_port, username=""):
    #     for user in all_users:
    #         if user["personal_port"] == personal_port:
    #             users_schema.delete_one({"personal_port"})



api.add_resource(MyApi, '/client','/client/<string:username>/<string:password>/<string:personal_port>')

if __name__ == "__main__":
    app.run(debug=True)


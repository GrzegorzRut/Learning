from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient

import bcrypt
import spacy
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://db:27017') #default mongo port
db = client.SimilarityDatabase
users = db["Users"]


def UserExist(username):
    nb_users = users.find({"Username":username}).count()
    return nb_users>0

def VerifyPassword(username,password):
    hashed_pw = users.find({"Username":username})[0]["Password"]
    pw_match = hashed_pw == bcrypt.hashpw(password.encode('utf8'),hashed_pw)
    return pw_match

def CountTokens(username):
     return users.find({"Username":username})[0]["Tokens"]

def UpdateTokens(username,num_tokens):
    users.update({"Username":username},
    {"$set":{"Tokens":num_tokens-1}}
    )
    pass

class Register(Resource):
    def post(self):        
        # step 1 get posted data by user
        postedData = request.get_json()
        
        # get the data
        username = postedData["username"]
        password = postedData["password"]
        
        if UserExist(username):
            retJson = {
                "status": 301,
                "msg": "Invalid Username"
            }
            return jsonify(retJson)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        # store username and pw into database
        users.insert({
        "Username": username,
        "Password": hashed_pw,
        "Tokens":6
        })
        retJson = {"status":200,
                   "msg":"You successfully signed up for the API"}
        return retJson

class Detect(Resource):
    def post(self):
        postedData = request.get_json()
        # get the data
        username = postedData["username"]
        password = postedData["password"]
        txt1 = postedData["txt1"]
        txt2 = postedData["txt2"]
       
        if not VerifyPassword(username,password):
            retJson = {
                "status": 302,
                "msg": "Invalid Username or Password"
            }
            return jsonify(retJson)

        if len(postedData)<4:
            retJson = {
                "status": 303,
                "msg": "Invalid Input (required 4 fields)"
            }
            return jsonify(retJson)

        num_tokens = CountTokens(username)

        if num_tokens < 1:
            retJson = {
                "status": 304,
                "msg": "No tokens left"
            }
            return jsonify(retJson)

        retJson = {"status":200,
                  "txt1": txt1,
                  "txt2": txt2,
                  "match": nlp(txt1).similarity(nlp(txt2))}
        
        UpdateTokens(username,num_tokens)
        return jsonify(retJson)

api.add_resource(Register,"/register")
api.add_resource(Detect,"/detect")

if __name__ == "__main__":
    app.run(host='0.0.0.0',port = 5000,debug = True)
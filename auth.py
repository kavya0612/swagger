from bson import json_util
from bson.objectid import ObjectId
from functools import wraps
import functools
from datetime import datetime
import json
from werkzeug.security import safe_str_cmp
from pymongo.errors import DuplicateKeyError
import pymongo
from werkzeug.local import LocalProxy
from flask_cors import CORS, cross_origin
from pymongo.errors import DuplicateKeyError, OperationFailure, BulkWriteError
from pymongo import MongoClient
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from flask import Flask, Blueprint, request, jsonify, g, make_response


client = MongoClient('mongodb+srv://Admin:admin123@cluster0.tefgx.mongodb.net/<test?retryWrites=true&w=majority')

db = client['test']
user= db['users']
apikeys = db["apikeys"]
cred = credentials.Certificate("serviceAccountKey.json")

#Initializing the firebase app
#firebase_admin.initialize_app(cred)

def login_required(func):
    @functools.wraps(func)
    def secure_func(*args, **kwargs):
        if(request.headers.get('Authorization')):  
            
            bearer =request.headers.get('Authorization')
            #bearer = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjA4MGU0NWJlNGIzMTE4MzA5M2RhNzUyYmIyZGU5Y2RjYTNlNmU4ZTciLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiZ293YWdlIiwicmVnIjp0cnVlLCJ0ZW5hbnRzIjpbeyJ0ZW5hbnRJZCI6Ijg5YTdiNzMxLThiYmEtNDg1YS1hMzcyLTkxOGFlZjM2NDAzNiIsInRlbmFudE5hbWUiOiJDYXNlbGV0cyIsInJvbGUiOiJFZGl0b3IifV0sImFjdGl2ZVRlbmFudCI6eyJ0ZW5hbnRJZCI6Ijg5YTdiNzMxLThiYmEtNDg1YS1hMzcyLTkxOGFlZjM2NDAzNiIsInRlbmFudE5hbWUiOiJDYXNlbGV0cyIsInJvbGUiOiJFZGl0b3IifSwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL2Nhc2VsZXRzLXYyLWZiLXRlc3QiLCJhdWQiOiJjYXNlbGV0cy12Mi1mYi10ZXN0IiwiYXV0aF90aW1lIjoxNjA5NDAxODE5LCJ1c2VyX2lkIjoiTlN4WGNlWlFYOFBUQTgzUnBUeUFMVlU1YzZ2MSIsInN1YiI6Ik5TeFhjZVpRWDhQVEE4M1JwVHlBTFZVNWM2djEiLCJpYXQiOjE2MDk0MDc4MjEsImV4cCI6MTYwOTQxMTQyMSwiZW1haWwiOiJnb3dhZ2U2MTg0QGNob21hZ29yLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7ImVtYWlsIjpbImdvd2FnZTYxODRAY2hvbWFnb3IuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGFzc3dvcmQifX0.vjbDEbTbd38vhwwwtywpd5HYiAvwFCH1QHUezwj9TBAQ-UHVDsONhcTKfLThdakZTvjLAOExhh103AnmewFvj5qRPyNqL_dnboAunZ_EL1wt8PTItTSusQK24b4943nrP181VWHWV8DXHGNn-NndqpwITFu6eoAroTNmnIE0kix_YtzRrTbNvMHhnOY2kUT4t89BKoA70lcmYk-0GHgeYnIoXtVm0KinBgOHROGeDmLLNBBi5fcroa7pSUIxq_QV_kJY3IRPf6zJT9rBnO_QolVeGB_CAwRMdZDsTFMOwOok9seqfNJAHobDb-uaBQf4aXWynLWOcXoiXw27jxOeqA"    
            token = bearer.split()[0]  # YourTokenHere
            try:
                decoded_token = auth.verify_id_token(token)
                #print(decoded_token)
                g.user = decoded_token
            
                return func(*args, **kwargs)
            except Exception as e:
                print("LOGIN REQUIRED EXCEPTION",e)
                return {"Error":"Could not create the document","Reason":"Incorrect User Token/ User Token expired"}
        else:
            return {"ERROR":"Authorization required"}
    return secure_func


def user_has_permission(access_level):
    def my_decorator(func):
        @functools.wraps(func)
        def secure_func(*args, **kwargs):
            if(request.headers.get('Authorization')):  
                bearer =request.headers.get('Authorization')
                token = bearer.split()[0]  # YourTokenHere
                try:
                    decoded_token = auth.verify_id_token(token)
                    email = decoded_token["email"]
                    doc = [doc for doc in db.users.find({"emailId":email})]
                    user = json.dumps(doc, default=json_util.default)
                    user = json.loads(user)
                    #print(user[0])    
                    user_role = user[0]['activeTenant']['role']
                    #user_role = decoded_token["activeTenant"]["role"]
                    if user_role in access_level:
                        #print(access_level)
                        return func(*args, **kwargs)
                    else:
                        return {"ERROR":"Permission required"}
                    
                except Exception as e:
                    print("EXCEPTION",e)
                    exception1 = "Could not create the document.  "+str(e)+ " is not specified"
                    return {"Error":exception1}
                
            else:
                return {"Access Denied":"Permission required"}
        return secure_func
    return my_decorator

def verify_api(func):
    @functools.wraps(func)
    def secure_func(*args, **kwargs):
        if(request.headers.get('apikey')):
            api_key = request.headers.get('apikey')
            doc = [doc for doc in db.apikeys.find({"apiKey":api_key})]
            #print(doc) #serializing the Cursor object
            key = json.dumps(doc, default=json_util.default)
            #print(users)
            key = json.loads(key)
            #print(key[0])    
            key_in_db = key[0]["apiKey"]
            print("KEY IN DATABASE ",key_in_db)
            print("API KEY ", api_key)
            if(api_key == key_in_db):
                
                return func(*args, **kwargs)
            else:
                return "Unauthorized access"
        else:
            return {"Required!":"API Key"}
            
    return secure_func

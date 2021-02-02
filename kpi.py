from mongoengine import *
from flask import Flask, Blueprint, request, jsonify, g, make_response
from kpi_schema import Kpi_Mongo, db
from subjects_schema import SubjectMaster, db
from helper import create_uuid
import datetime as dt
import json
from bson import json_util
from bson.objectid import ObjectId
from pprint import pprint
import pymongo
from flask_cors import CORS
from flask_restful import Resource, Api, abort
from functools import wraps
from werkzeug.security import safe_str_cmp
from pymongo.errors import DuplicateKeyError
import pymongo
from werkzeug.local import LocalProxy
from flask_cors import CORS, cross_origin
from pymongo.errors import DuplicateKeyError, OperationFailure, BulkWriteError
from auth import verify_api, login_required, user_has_permission
from slugify import Slugify
from pymongo import MongoClient , WriteConcern, ReadPreference
from pymongo.errors import ConfigurationError, OperationFailure, ConnectionFailure
from pymongo.read_concern import ReadConcern
from flask_mongoengine import MongoEngine
import time
from datetime import timedelta
from flask_swagger_ui import flask_swagger_ui,get_swaggerui_blueprint


app = Flask(__name__)

cors = CORS(app)
app.config['PROPAGATE_EXCEPTIONS'] = True


app.config['CORS_HEADERS'] = 'Content-Type'

custom_slugify = Slugify(to_lower=True)
custom_slugify.separator = '_' 



SWAGGER_URL = '/swagger'
API_URL = '/static/kavya0612-view-kpi-1.0.0-resolved.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "View KPI"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

mongo = MongoEngine()
client = db['kpi']
wc_majority = WriteConcern("majority", wtimeout=1000)
    #wc_majority = WriteConcern("majority", wtimeout=1000)
def run_transaction_with_retry(txn_func, session):
    while True:
        try:
            txn_func(session)  # performs transaction
            break
        except (ConnectionFailure, OperationFailure) as exc:
            # If transient error, retry the whole transaction
            if exc.has_error_label("TransientTransactionError"):
                print("TransientTransactionError, retrying "
                      "transaction ...")
                continue
            else:
                raise
def commit_with_retry(session):
    while True:
        try:
            # Commit uses write concern set at transaction start.
            session.commit_transaction()
            transaction_status = "Transaction committed."
            #print(transaction_status)
            return transaction_status
            break
        except (ConnectionFailure, OperationFailure) as exc:
            # Can retry commit
            if exc.has_error_label("UnknownTransactionCommitResult"):
                print("UnknownTransactionCommitResult, retrying "
                      "commit operation ...")
                continue
            else:
                print("Error during commit ...")
                raise
                
                
                

@app.route('/kpi/create', methods=['POST'])
@login_required
@user_has_permission(["Admin","Editor"])
@cross_origin()
def create_kpi():
    start_time = time.time()
    transaction = request.args.get('transaction') 
    data = request.get_json()
        
    
    name = data['name']
    slug = custom_slugify(data['name'])
    type = data['type']
    cat = data['cat']
    #print("USER DETAILS",g.user['activeTenant'])
    tenantId = g.user['activeTenant']['tenantId']
    uid = g.user['uid']
    createdBy = uid
    updatedBy = uid

    
    type_format = data['type'].split(":")
    type_main = type_format[0]
    if(len(type_format) > 1):
        type_sub = type_format[1]
    else:
        type_sub = type_format[0]

    try:           
        if 'subjects' in data:    
            subjects = data['subjects']
        else:
            subjects = []

        if 'units' in data:
            units = data['units']
        else:
            units = []
            
        if 'other_names' in data:
            other_names = data['other_names']
        else:
            other_names = []

        if 'desc' in data:
            desc = data['desc']
        else:
           desc = "" 
        
        if 'notes' in data:
            notes = data['notes']
        else:
            notes = data['desc']
           
        if 'original' in data:
            original = data['original']
        else:
           original = data['name']

        if 'numerator' in data:
            numerator = data['numerator']
        else:
           numerator = "" 

        if 'denominator' in data:
            denominator = data['denominator']
        else:
           denominator = ""    

        if 'formula' in data:
            formula = data['formula']
        else:
           formula = "" 

        if 'status' in data:
            status = data['status']
        else:
            status = "Draft"

      
        if 'positive_indicator' in data:
            positive_indicator = data["positive_indicator"]
            if(positive_indicator == "High"):
                positive = {
                    "indicator" : "High",
                    "change":"Increase"
                }
                negative = {
                "indicator" : "Low",
                "change":"Decrease"
                }
                
                k = "increase_kpi"
                v = slug
                Code= slug
                P_or_C = "P"
                Name =  data["name"]
                Parent_code = ""


            elif(positive_indicator == "Low"):
                positive = {
                    "indicator" : "Low",
                    "change":"Decrease"
                }
                negative = {
                    "indicator" : "High",
                    "change":"Neutral"
                }

                k = "decrease_kpi"
                v = slug
                Code= slug
                P_or_C = "P"
                Name =  data["name"]
                Parent_code = ""
            else:
                positive = {
                    "indicator" : "Neutral",
                    "change":"Decrease"
                }
                negative = {
                    "indicator" : "Neutral",
                    "change":"Neutral"
                }

                
    except:
        pass
    
    print(Code)
    message = {}
        
    try:
        kpidata = Kpi_Mongo(
            kpi_id = create_uuid(),
            tenantId = tenantId,
            name = name,
            desc = desc,
            notes = notes,
            original = original,
            other_names = other_names,
            status = status,
            slug = slug,
            type = type,
            type_main = type_main,
            type_sub = type_sub,
            cat = cat,
            units = units,
            numerator = numerator,
            denominator = denominator,
            formula = formula,
            positive_indicator = positive_indicator,
            positive = positive,
            negative = negative,
            subjects = subjects,
            createdBy = createdBy,
            updatedBy = updatedBy)
    
        subjectsdata = SubjectMaster(Name = Name,
            Parent_code = Parent_code,
            Code = Code,
            P_or_C= P_or_C,
            k = k,
            v = v)
        
            
    except:
    #
        message = "Required field is not specified"
    
    if(transaction == "false"):  
        try:    
            kpidata.save() 
            subjectsdata.save()
            message = {"Success1":"Kpi is Created"}
            message1 = {"Success2":"subjects is Created"}
            message.update(message1)
            print(message)
        
        except:
            message = {"DuplicateKeyError": "Kpi already exists in the db collection"}
            message1 = {"DuplicateKeyError1": "subject already exists in the db collection"}
            print("DUP KEY",message)
            message.update(message1)
            print(message)
                
       
      
        
        
    elif(transaction == "true"):
        def main_insert_transaction(session):
                
                session.start_transaction(
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority"),
                read_preference=ReadPreference.PRIMARY )
            
                
                kpidata.save()
                subjectsdata.save()
                
                
                commit_with_retry(session)
            
        with db.start_session() as session:
        
            try:
                run_transaction_with_retry(main_insert_transaction, session)  
                
                message = "Transaction Committed"
                                                
            except Exception as exc:
                session.abort_transaction()
                abort_error = str(exc)
                print(abort_error)
                message = "Caught exception during transaction, aborting  "+abort_error
                
    elapsed_time_secs = time.time() - start_time   
    msg = "Execution took: %s secs (Wall clock time)" % timedelta(seconds=round(elapsed_time_secs))

    print(msg)
    return {"Message":message,
            "time taken":elapsed_time_secs}  
   
    
@app.route("/kpi/view-kpi", methods=['GET'])
@cross_origin()

def view_kpi():
    
    name = request.args.get('name')
    name = name.strip()   
    q_set = Kpi_Mongo.objects(name = name)
    json_data = q_set.to_json()
    dicts = json.loads(json_data)
    return {"data":dicts}


"""
@app.route('/caselet/update', methods=['POST'])
@login_required
#@user_has_permission(["Admin","Editor"])
@cross_origin()
def update_caselet():
    try:
        tenantId = g.user['activeTenant']['tenantId']
        uid = g.user['uid']
        identifier = request.args.get('identifier') 
        print(identifier)
        #print(tenantId)
        #transaction = request.args.get('transaction') 
        data = request.data
        print(data)
    except:
       message = {"Error":"Required field is not specified"}
    
    try:
        hascaselet = CaseletMains.objects(identifier = identifier).get()#),tenantId = tenantId).get()
        print(hascaselet)
    except:
        message = {"Error":"Caselet with given id doesn't exist"}
        return message
    audit = {
        "createdBy":hascaselet.audit['createdBy'],
        "createdDt":hascaselet.audit['createdDt'],
        "updatedBy":uid,
        "updatedDt":dt.datetime.now()
            }
    
    print(audit)
    name = data['name']
    
    slug = custom_slugify(data['name'])
    
    
    if hascaselet:
            updatedata = CaseletMains.objects(identifier = identifier).update(**data,
                name = name,
                slug = slug,
                audit = audit
                 )
            print(updatedata)
            
            return "Success"

#working 
data = json.dumps(data)
kpi = Kpi_Mongo.from_json(data)
kpi.save()


di = {
    "entityCat" : "Collection",
        "entityType" : "Master Collection",
        "masterName" : data['masterName'],
        "masterId" : "",
        "slug":"sklkc"}
data.update(di)
data = json.dumps(data)
collectiondata = CaseletMains.from_json(data)

collectiondata.save()
Out[80]: <CaseletMains: CaseletMains object>
""" 

if __name__=="__main__":
    app.run(port=5000, debug=True,use_reloader=False)   

    


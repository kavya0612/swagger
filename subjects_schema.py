from mongoengine import *
import datetime as dt

db = connect(host = 'mongodb+srv://Kavya:kavya123@cluster0.6nikz.mongodb.net/<dbname>?retryWrites=true&w=majority')


class SubjectMaster(Document):
    Name = StringField()
    Parent_code = StringField()
    Code = StringField()
    P_or_C = StringField()
    k = StringField()
    v = StringField()

#initial_doc = SubjectMaster(Name = "New subject",Parent_code = "",Code = "new_subject",P_or_C="P",k = "industry",v = "retail").save()

from mongoengine import *
import datetime as dt

db = connect(host = 'mongodb+srv://Kavya:kavya123@cluster0.6nikz.mongodb.net/<dbname>?retryWrites=true&w=majority')


class Subjects(EmbeddedDocument):
    k = StringField()
    v= StringField()
    
class Positive(EmbeddedDocument):
    indicator = StringField()
    change = StringField()

class Negative(EmbeddedDocument):
    indicator = StringField()
    change = StringField()    

class Tracking(EmbeddedDocument):
    views = IntField(default=0)
       
class Kpi_Mongo(Document):
    kpi_id = StringField()
    tenantId = StringField()
    name = StringField(required=True,max_length=100)
    slug = StringField()
    status = StringField(default="Draft")
    version = IntField(default=1)
    original = StringField()
    owner = StringField(default="system")
    workspace = StringField(default="default")
    notes = StringField()
    formula = StringField()
    numerator = StringField()
    denominator = StringField()
    positive_indicator = StringField()
    positive = EmbeddedDocumentField(Positive)
    negative = EmbeddedDocumentField(Negative)
    tracking = EmbeddedDocumentField(Tracking)
    subjects = ListField(EmbeddedDocumentField(Subjects),default=list)
    cat= StringField(required=True)
    type= StringField(required=True)
    type_main = StringField()
    type_sub = StringField()
    statusChangeDate = DateTimeField(default=dt.datetime.now())
    desc = StringField(max_length=500)
    createdBy = StringField(default="")
    updatedBy = StringField(default="")
    createdDt = DateTimeField(default=dt.datetime.now())
    updatedDt = DateTimeField(default=dt.datetime.now())
    other_names = ListField(default=list)
    units = ListField()
    
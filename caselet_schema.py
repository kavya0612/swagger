from mongoengine import *
import datetime as dt

db = connect(host = 'mongodb+srv://Kavya:kavya123@cluster0.6nikz.mongodb.net/<dbname>?retryWrites=true&w=majority')


class Subject(EmbeddedDocument):
    k = StringField()
    v= StringField()
    
class Access(EmbeddedDocument):
    shareable = BooleanField(default=False)
    web = BooleanField(default=False)
    internal = BooleanField(default=True)
    shareableWithPwd = BooleanField(default=False) 
    

class Media(EmbeddedDocument):
    use = BooleanField(default=False)
    url = StringField(default="")
    cat = StringField(default="")
    type = StringField(default="") 
    thumbnailUrl = StringField(default="")
   
    
class Audit(EmbeddedDocument):
     createdBy = StringField(default="")
     updatedBy = StringField(default="")
     createdDt = DateTimeField(default=dt.datetime.now())
     updatedDt = DateTimeField(default=dt.datetime.now())
    
class CaseletMains(Document):
    identifier = StringField()
    tenantId = StringField()
    name = StringField(required=True,max_length=100)
    slug = StringField()
    status = StringField(default="Draft")
    version = IntField(default=1)
    masterId = StringField(default="")
    masterName= StringField(required=True)
    entityCat = StringField(required=True)
    entityType = StringField()
    access = EmbeddedDocumentField(Access)
    media = EmbeddedDocumentField(Media)
    subjects = ListField(EmbeddedDocumentField(Subject),default=list)
    coverageCat= StringField(default="")
    coverageType= StringField(default="")
    cat= StringField(required=True)
    typ= StringField(required=True)
    caselets = ListField(default=list)
    statusChangeDate = DateTimeField(default=dt.datetime.now())
    about = StringField(max_length=500)
    startDt = DateTimeField(default=dt.datetime.now())
    endDt = DateTimeField(default=None)
    audit = EmbeddedDocumentField(Audit)
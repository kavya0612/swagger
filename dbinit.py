from kpi_schema import Kpi_Mongo

initial_doc = Kpi_Mongo(name = "New kpi",cat = "organization",type = "money:revenue",type_main="money",type_sub = "revenue").save()

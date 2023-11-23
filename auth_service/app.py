from mongoengine import connect, Document, DateTimeField, StringField
from datetime import datetime

user = "session_user"
pwd = "session_pwd"
port = 27018
db_name = "session_auth"
host = "localhost"

con_string = f"mongodb://{user}:{pwd}@{host}:{port}/{db_name}"
connect(host=con_string)

class User(Document):
    username = StringField(required=True)
    email = StringField(required=True)
    # I guess if logged in with google it wont be required ... ? 
    password = StringField() 
    stream_key = StringField(required=True)
    key_exp_date = DateTimeField()
    last_authenticated = DateTimeField()


u = User.objects().first()
u.last_authenticated = datetime.now().isoformat()
u.save()

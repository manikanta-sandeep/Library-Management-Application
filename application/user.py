from .models import user
from .database import db 
from base64 import b64encode
from .list_operations import make_2blobs
from .nophoto import images

class user_registrations:
    def __init__(self,email,name,dob,password):
        self.email=email
        self.name=name
        self.dob=dob
        self.password=password
    
    def register_user(self):
        new_user=user(name=self.name,email=self.email,dob=self.dob,password=self.password)
        db.session.add(new_user)
        db.session.commit()
        user_created=user.query.filter(user.email==self.email).one()
        return user_created.user_id

    def update_user(self,email):
        pass

class updations:

    def update_password(self,email,password):
        new_user=db.session.execute("update user set password=:pwd where email=:mail",{"pwd":password,"mail":email})
        db.session.commit()
        username=db.session.execute("select name from user where email=:mail",{"mail":email})
        for i in username:
            return i[0]
    
    
    def new_user_registration(self,email,pwd):
        count_record=db.session.execute("select count(*) from user where email=:mail",{"mail":email})
        for i in count_record:
            count=i[0]
        if count==0:
            db.session.execute("insert into user(email,password) values (:email,:pwd)",{"email":email,"pwd":pwd})
        else:
            db.session.execute("update user set password=:pwd where email=:mail",{"mail":email,"pwd":pwd})
        db.session.commit()
        return 
    
    def user_registration(self,email,name,bday,pwd):
        db.session.execute("update user set name=:name,dob=:bday,password=:pwd,profile_picture=:pic where email=:mail",{"mail":email,"name":name,"bday":bday,"pwd":pwd,"pic":images().noimage()})
        db.session.commit()
        return 
    
    

class user_data:
    def all_users(self,key):
        if key==0:
            user_data=db.session.execute('SELECT * from user')
        elif key==1:
            user_data=db.session.execute('SELECT * from user where user_privileges=1')
        data=[]
        for i in user_data:
            if i.user_privileges==0:
                su="Normal User"
            elif i.user_privileges==1:
                su="Super User"
            elif i.user_privileges==2:
                su="Student"
            data+=[[i.user_id ,i.name ,i.email ,i.dob,i.password , b64encode(i.profile_picture).decode("utf-8") ,su ]]
        data=make_2blobs(data)
        return data
    
from .models import user
from .database import db

class checking:
    def isredundant(self,email):
        try:
            current_user=user.query.filter(user.email==email).one()
            return True
        except:
            return False

    def isnotuser(self,email_id,password):
        try:
            current_user=user.query.filter(user.email==email_id).one()
            if current_user.password==password:
                return True,current_user.name,current_user.user_privileges
            else:
                return False,False,False
        except:
            return False,False,False 
    
    def check_password_forgot_user(self,email):
        a=db.session.execute("select count(*) from user where email=:mail",{"mail":email})
        for i in a:
            count=i[0]
        return count
        
'''    def issuperuser(self,email):
        get_email_id=email
        try:
            current_user=superuser.query.filter(superuser.email==get_email_id).one()
            return 1
        except:
            return 0'''
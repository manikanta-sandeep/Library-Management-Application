import smtplib
import time
import email
import random
from .database import db

from .user import updations
from .user_checking import checking

class emailing:
    def generate_password(self):
        l1=[]
        for i in range(10):
            l1+=[str(i)]
        for i in range(26):
            l1+=[chr(i+65),chr(i+97)]
        password=""
        for i in range(8):
            password+=random.choice(l1)
        return password

    
    def new_user_email(self,email):
        gp=emailing().generate_password()
        updations().new_user_registration(email,gp)
        msg=f'''
Hi ,

Thank you for registering your account on PROJECT SRP. Hope you will find it easier to use. Here is the verification code, please verify your account with the below verification code.


{gp}

Thanks and Regards
Manikanta Sandeep
Team Project SRP.
        '''
        emailing().email("Verification code for account sign up",email,msg)

    def forgot_password(self,email):
        a=checking().check_password_forgot_user(email)
        if a==0:
            return 1
        gp=emailing().generate_password()
        ur=updations()
        username=ur.update_password(email,gp)
        
        msg=f'''
Hi {username},

You have requested to reset your password. Please find the password below.

{gp}

Thanks and Regards,
Team Project SRP.
        '''

        emailing().email("Forgot Password",email,msg)
        return
    
    def contactadmin(self,mail,name,subject,msg):
        message=f'''
Hi Admin,

There is a query from {name}
    Name    : {name}
    Email   : {mail}

Message:

{msg}

Thanks and Regards,
Team Project SRP.
        '''
        emailing().email(subject,"projectsrp.manikanta@gmail.com",message)
        return


    def email(self,subject,reciever,msg):
        ################# SMTP SSL ################################
        start = time.time()
        try:
            smtp_ssl = smtplib.SMTP_SSL(host="smtp.gmail.com", port=465)
        except Exception as e:
            print("ErrorType : {}, Error : {}".format(type(e).__name__, e))
            smtp_ssl = None

        print("Connection Object : {}".format(smtp_ssl))
        print("Total Time Taken  : {:,.2f} Seconds".format(time.time() - start))

        ######### Log In to mail account ############################
        print("\nLogging In.....")
        resp_code, response = smtp_ssl.login(user="projectsrp.manikanta@gmail.com", password="camqcojiyaxiisbn")

        print("Response Code : {}".format(resp_code))
        print("Response      : {}".format(response.decode()))

        ################ Send Mail ########################
        print("\nSending Mail..........")

        message = email.message.EmailMessage()
        message.set_default_type("text/plain")

        frm = "Project SRP"
        to_list = [reciever]
        message["From"] = frm
        message["To"] = to_list
        message["Subject"] = subject

        message.set_content(msg)

        response = smtp_ssl.sendmail(from_addr=frm,
                                    to_addrs=to_list,
                                    msg=message.as_string())

        print("List of Failed Recipients : {}".format(response))

        ######### Log out to mail account ############################
        print("\nLogging Out....")
        resp_code, response = smtp_ssl.quit()

        print("Response Code : {}".format(resp_code))
        print("Response      : {}".format(response.decode()))
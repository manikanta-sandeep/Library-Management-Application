from email import message
import re
from flask import render_template, redirect,request,session,flash
from flask import current_app as app
from .models import user
from .user_checking import checking
from .user import updations, user_registrations,user_data
from .book_registrations import book_registrations,book_search,student,book_deletion,book_queries
from base64 import b64encode
from .request_registrations import fine_operations, request_operations, student_request, history_transactions
from .database import db
from .mail import emailing

b_list=[["All books","/Home/All_books"],["Add a book","/Home/Add_a_book/"],["Delete a book","/Home/Delete_a_book"],["Requests","/Home/Requests"],["Transactions","/Home/Transactions"],["Fines","/Home/Fines"],["Update book details","/Home/Update_book_details"],["Make not available","/Home/make_not_available"],["Query Executer","/Home/Query_Executer"]]    
b_list2=[["Take a book","/Home/Student/Take_a_book/"],["Give a book","/Home/Student/Give_a_book/"],["Books Status","/Home/Student/Book_Status"],["Pay Fine","/Home/Student/Pay_Fines"],["Fines","/Home/Student/Fines"],["Cart","/Home/Student/Cart"],["History","/Home/Student/History"]]
sublist=[["Added a Book","/Home/Added_a_book/"],["Select a Book","/Home/Select_a_book"],["Deleted a Book","/Home/Deleted_a_book"],["Deleted all Books","/Home/Delete_all"],["All books Deleted","/Home/Deleted_all"],["Book Requests","/Home/Requests/book_requests"],["Return Requests","/Home/Requests/return_requests"]]
sublist2=[["Cart","/Home/Student/Clear_all"]]
button_list=b_list,sublist
button_list2=b_list2,sublist2

@app.route("/", methods=["GET","POST"])
def index_page():
    db.session.commit()
    return render_template("index_page.html")
'''
@app.route("/",methods=["GET","POST"])
def testing():
    ud=user_data()
    data=ud.all_users()
    return render_template("test.html",data=data)
'''
@app.route("/login/", methods=["GET","POST"], defaults={"message":None})
@app.route("/login/<message>", methods=["GET","POST"])
def login_page(message):
    if message!=None:
        return render_template("login_page.html", message=message)
    else:
        return render_template("login_page.html")

@app.route("/check/", methods=["POST"])
def user_verified():
    if request.method=="POST":
        email_id=request.form["email"]
        user_password=request.form["password"]
        chk=checking()
        a=chk.isnotuser(email_id,user_password)
        if a[0]:
            session["email"]=request.form["email"]
            session["superuser"]=a[2]
            session["name"]=a[1]
            return redirect("/Home/")
        else:
            return redirect("/login/password is incorrect")

@app.route("/new_user_login", methods=["GET"])
def new_registration():
    return render_template("user_verification.html",key=1)

@app.route("/user_creation",methods=["POST","GET"])
def user_create():
    if request.method=="POST":
        msg=0
        mail=request.form["email"]
        emailing().new_user_email(mail)
        session["temp_email"]=mail
    else:
        msg=1
    return render_template("user_verification.html",key=2,mail=session["temp_email"],message=msg)

@app.route("/update_details",methods=["GET","POST"])
def new_user_details_update():
    a=checking().isnotuser(session["temp_email"],request.form["password"])
    if a[0]:
        return render_template("new_user_login.html",mail=session["temp_email"])
    else:
        return redirect("/user_creation") 


@app.route("/logout", methods=["GET","POST"])
def logout():
    session.clear
    return redirect("/login/")

@app.route("/Home/", methods=["GET","POST"])
def home():
    if session["superuser"]==1:
        btn_list=button_list
        return render_template("1.2home.html",dkey=-1,disablekey=1,current_path="/Home/",button_list=btn_list,username=session["name"],key=session["superuser"])     
    else:
        return redirect("/Home/Student/")
@app.route("/Home/All_books",methods=['GET','POST'])
def all_books():
    bg=book_search()
    data=bg.search()
    return render_template("1.2home.html",data=data,dkey=0,disablekey=1, current_path="/Home/All_books",button_list=button_list, username=session["name"],key=session["superuser"])


@app.route("/Home/Add_a_book/",methods=["GET","POST"])
def Add_a_book():
    return render_template("1.2home.html", akey=0,dkey=1,disablekey=1,current_path="/Home/Add_a_book/",button_list=button_list, username=session["name"],key=session["superuser"])     

@app.route("/Home/Added_a_book/", methods=["GET","POST"])
def added_a_book():
    name=request.form["Book_Name"]
    authors=request.form["Book_Authors"]
    copies=request.form["Book_Copies"]
    edition=request.form["Book_Edition"]
    picture1=request.files["Book_Picture"]
    picture=picture1.read()
    reg=book_registrations()
    if reg.isavailable(name,edition):
        AvailableKey=0
        bookData=reg.register_book(name,authors,copies,edition,picture)

    else:
        return render_template("1.2home.html", akey=1,dkey=1,disablekey=1,current_path="/Home/Add_a_book/",button_list=button_list, username=session["name"],key=session["superuser"])     
    return render_template("1.2home.html",  book_data=bookData,dkey=1,disablekey=1,current_path="/Home/Added_a_book/",button_list=button_list, username=session["name"],key=session["superuser"])
    


@app.route("/Home/Delete_a_book",methods=["GET","POST"])
def Delete_a_book():
    bg=book_search()
    available_books=bg.total_available()
    operations=[available_books]
    return render_template("1.2home.html",dkey=2,disablekey=1,current_path="/Home/Delete_a_book",button_list=button_list,operation=operations, username=session["name"],key=session["superuser"])     

@app.route("/Home/Select_a_book",methods=["POST"])
def Select_a_book():
    option=request.form["option"]
    pattern=request.form["pattern"]
    bg=book_search()
    data=bg.search(option,pattern)
    return render_template("1.2home.html", dkey=2,disablekey=1,data=data,current_path="/Home/Select_a_book",button_list=button_list, username=session["name"],key=session["superuser"])     

@app.route("/Home/Deleted",methods=["POST"])
def book_deleted():
    info=request.form["book_info"]
    bd=book_deletion()
    data=bd.delete_a_book(info)
    return render_template("1.2home.html", data=data, dkey=2,disablekey=1,current_path="/Home/Deleted",button_list=button_list, username=session["name"],key=session["superuser"])     

@app.route("/Home/Delete_all/", methods=["POST"])
def delete_all():
    bg=book_search()
    available_books=bg.total_available()
    operations=[available_books]
    return render_template("1.2home.html", dkey=2,disablekey=1,current_path="/Home/Delete_all",button_list=button_list,operation=operations, username=session["name"],key=session["superuser"])     


@app.route("/Home/Deleted_all/", methods=["POST"])
def deleted_all():
    da=book_deletion()
    da.delete_all()
    bg=book_search()
    available_books=bg.total_available()
    operations=[available_books]
    return render_template("1.2home.html", dkey=2,disablekey=1,current_path="/Home/Deleted_all",button_list=button_list,operation=operations, username=session["name"],key=session["superuser"])     

@app.route("/Home/Requests",methods=["GET","POST"])
def all_requests():
    return render_template("1.2home.html",dkey=3,disablekey=1,current_path="/Home/Requests",button_list=button_list, username=session["name"],key=session["superuser"])

@app.route("/Home/Requests/book_requests", methods=["GET","POST"])
def book_requests():
    st=student_request()
    data=st.all_book_requests()
    return render_template("1.2home.html",data=data,dkey=3,disablekey=1,current_path="/Home/Requests/book_requests",button_list=button_list, username=session["name"],key=session["superuser"])


@app.route("/Home/Requests/return_requests", methods=["GET","POST"])
def return_requests():
    st=student_request()
    data=st.all_return_requests()
    return render_template("1.2home.html",data=data,dkey=3,disablekey=1,current_path="/Home/Requests/return_requests",button_list=button_list, username=session["name"],key=session["superuser"])


@app.route("/Home/Accept_book_Request",methods=["GET","POST"])
def accept_book_request():
    serial_no=request.form["serial_info"]
    ro=request_operations()
    ro.accept_book_request(serial_no)
    return redirect("/Home/Requests/book_requests")

@app.route("/Home/Accept_Return_Request",methods=["GET","POST"])
def accept_return_request():
    serial_no=request.form["serial_info"]
    ro=request_operations()
    ro.accept_return_request(serial_no)
    return redirect("/Home/Requests/return_requests")

@app.route("/Home/Transactions", methods=["GET","POST"])
def Transactions():
    return render_template("1.2home.html",dkey=4,disablekey=1,current_path="/Home/Transactions",button_list=button_list, username=session["name"],key=session["superuser"])

@app.route("/Home/Transactions/Deleted", methods=["GET","POST"])
def transactions_deleted():
    sr=student_request()
    sr.clear_transactions()
    return redirect("/Home/")

@app.route("/Home/Fines",methods=["GET","POST"])
def fines():
#    sr=student_request().delete_transaction()
    data=fine_operations().all_fines()
    return render_template("1.2home.html",data=data,disablekey=1,dkey=5,current_path="/Home/Fines",button_list=button_list, username=session["name"],key=session["superuser"])

@app.route("/Home/Update_book_details",methods=["GET","POST"])
def update_book_details():
    return render_template("1.2home.html",dkey=6,disablekey=1,current_path="/Home/Update_book_details",button_list=button_list, username=session["name"],key=session["superuser"])

@app.route("/Home/make_not_available",methods=["GET","POST"])
def make_not_available():
    bg=book_search()
    available_books=bg.total_available()
    operations=[available_books]
    return render_template("1.2home.html",dkey=7,disablekey=1,current_path="/Home/make_not_available",button_list=button_list,operation=operations, username=session["name"],key=session["superuser"])

@app.route("/Home/make_not_available/pick_a_book",methods=["GET","POST"])
def make_not_available_pick():
    option=request.form["option"]
    pattern=request.form["pattern"]
    bg=book_search()
    data=bg.search(option,pattern)
    return render_template("1.2home.html", dkey=7,disablekey=1,data=data,current_path="/Home/make_not_available/pick_a_book",button_list=button_list, username=session["name"],key=session["superuser"])     


@app.route("/Home/make_not_available/make_with_id",methods=["GET","POST"])
def make_not_available_make():
    info=request.form["id"]
    bg=book_registrations().make_no_available(info,1)
    available_books=bg.total_available()
    operations=[available_books]
    return render_template("1.2home.html",dkey=7,disablekey=1,current_path="/Home/make_not_available",button_list=button_list,operation=operations, username=session["name"],key=session["superuser"])


@app.route("/Home/Query_Executer",methods=["GET","POST"])
def queries():
    return render_template("1.2home.html",dkey=8,disablekey=1,current_path="/Home/Query_Executer",button_list=button_list, username=session["name"],key=session["superuser"])

@app.route("/Home/Query_Executer2",methods=["GET","POST"])
def queries2():
    flash("Query sent")
    a=request.form["query"]
    data=book_queries().query_execute(a)
    return render_template("1.2home.html",dkey=8,disablekey=1,query=a,data=data,current_path="/Home/Query_Executer",button_list=button_list, username=session["name"],key=session["superuser"])


@app.route("/Home/Student/", methods=["GET","POST"])
def students():
    return render_template("1.2home.html",disablekey=1,current_path="/Home/Student/",button_list=button_list2, username=session["name"],key=session["superuser"])     

@app.route("/Home/Student/Take_a_book/", methods=["GET","POST"])
def take_a_book():
    s=student()
    data=s.Take_a_book(session["email"])
    return render_template("1.2home.html",dkey=0, data=data, disablekey=1,na=0,current_path="/Home/Student/Take_a_book/",button_list=button_list2, username=session["name"],key=session["superuser"])     

@app.route("/Home/Student/Give_a_book/", methods=["GET","POST"])
def give_a_book():
    sr=student_request()
    data=sr.student_books_taken(session["email"])
    return render_template("1.2home.html", data=data,dkey=1, disablekey=1,na=0,current_path="/Home/Student/Give_a_book/",button_list=button_list2, username=session["name"],key=session["superuser"])

@app.route("/Home/Student/Give_a_book/Requested", methods=["GET","POST"])
def student_return_request():
    serial_no=request.form["serial_info"]
    rq=request_operations()
    #print(serial_no)
    rq.make_a_return_request(int(serial_no))
    return redirect("/Home/Student/Give_a_book/")

@app.route("/Home/Student/Book_Status", methods=["GET","POST"])
def status():
    data=student_request().student_book_status(session["email"])
    #print(data)
    return render_template("1.2home.html", disablekey=1,na=0 ,dkey=2,data=data,current_path="/Home/Student/Book_Status",button_list=button_list2, username=session["name"],key=session["superuser"])     

@app.route("/Home/Student/Book_Status/Information", methods=["GET","POST"])
def status_info():
    t_id=request.form["info"]
    #print(t_id)
    data=student_request().status_information(int(t_id))
    return render_template("1.2home.html", disablekey=1,na=0 ,dkey=2,data=data ,current_path="/Home/Student/Book_Status/Information",button_list=button_list2, username=session["name"],key=session["superuser"])     

@app.route("/Home/Student/Clear_all", methods=["GET","POST"])
def clear_cart():
    bd=book_deletion()
    bd.clear_cart()
    return render_template("1.2home.html", disablekey=1,na=0 ,dkey=5,current_path="/Home/Student/Clear_all",button_list=button_list2, username=session["name"],key=session["superuser"])     


@app.route("/Home/Student/Take_a_book/added_to_cart", methods=["GET","POST"])
def take_a_book_and_added():
    info=request.form["book_info"]
    cart_book_id=int(info)
    s=student().add_to_cart(session["email"],cart_book_id)
    return redirect("/Home/Student/Take_a_book/")

@app.route("/Home/Student/Cart",methods=["GET","POST"])
def cart_items():
    s=student()
    data=s.cart_books(session["email"])
    return render_template("1.2home.html",disablekey=1,na=0 ,dkey=5,data=data,current_path="/Home/Student/Cart",button_list=button_list2, username=session["name"],key=session["superuser"])     

@app.route("/Home/Student/Cart/remove_book",methods=["GET","POST"])
def remove_cart_book():
    bd=book_deletion()
    bd.delete_a_cart_book(session["email"],int(request.form["book_info"]))
    return redirect("/Home/Student/Cart")

@app.route("/Home/Student/make_request", methods=["GET","POST"])
def make_a_request():
    cart_book_id=int(request.form["book_info"])
    user_id=session["email"]
    ro=request_operations()
    ro.register_a_request(user_id,cart_book_id)
    return redirect("/Home/Student/Cart")

@app.route("/Home/Student/Fines", methods=["GET","POST"])
def student_fines():
    data=fine_operations().student_fines(session["email"])
    return render_template("1.2home.html",disablekey=1,na=0 ,dkey=4,data=data,current_path="/Home/Student/Fines",button_list=button_list2, username=session["name"],key=session["superuser"])     
 

@app.route("/Home/Student/Pay_Fines", methods=["GET","POST"])
def student_pay_fine():
    return render_template("1.2home.html",disablekey=1,na=0 ,dkey=3,current_path="/Home/Student/Pay_Fines",button_list=button_list2, username=session["name"],key=session["superuser"])     
 

@app.route("/Home/Student/History", methods=["GET","POST"])
def student_history():
    ht=history_transactions()
    data=ht.history(session["email"])
    return render_template("1.2home.html",disablekey=1,na=0 ,dkey=6,data=data,current_path="/Home/Student/History",button_list=button_list2, username=session["name"],key=session["superuser"])     

@app.route("/Home/Student/History/Information", methods=["GET","POST"])
def student_history_info():
    t_id=request.form["info"]
    data=student_request().history_information(int(t_id))
    return render_template("1.2home.html",disablekey=1,na=0 ,dkey=6,data=data,current_path="/Home/Student/History/Information",button_list=button_list2, username=session["name"],key=session["superuser"])     


@app.route("/Home/Student/History/Clear", methods=["GET","POST"])
def student_history_clear():
    ht=history_transactions()
    ht.clear_history()
    return redirect("/Home/Student/History")



@app.route("/Dashboard/", methods=["GET","POST"])
def dashboard():
    return render_template("1.2home.html",tkey=0,current_path="/Dashboard/", username=session["name"],key=session["superuser"])

@app.route("/Work/", methods=["GET","POST"])
def work():
    return render_template("1.2home.html",tkey=1,current_path="/Work/", username=session["name"],key=session["superuser"])

@app.route("/all_users/", methods=["GET","POST"])
def all_users():
    ud=user_data()
    data=ud.all_users(0)
    return render_template("4content.html",tkey=0, username=session["name"], blob_data=data,key=session["superuser"], data=data)

@app.route("/superusers/", methods=["GET","POST"])
def all_superusers():
    ud=user_data()
    data=ud.all_users(1)
    return render_template("4content.html",tkey=1, username=session["name"], blob_data=data,key=session["superuser"], data=data)

'''
@app.route("/sessions/", methods=["GET","POST"])
def session_page():
    data=session.query.all()
    blob_data=make_3blobs(data)
    return render_template("5sessions.html", username=session["name"],blob_data=blob_data, data=data, length=len(data),key=session["superuser"])
'''
@app.route("/update2/", methods=["GET","POST"])
def update():
    user_data=user.query.filter(user.email==session["email"]).one()
    
    try:
        a=request.form["name"]
        keyname=1
    except:
        keyname=0
    try:
        b=request.form["dob"]
        keydob=1
    except:
        keydob=0
    try:
        c=request.form["picture"]
        keypicture=1
    except:
        keypicture=0
    return render_template("6update.html",tkey=0, username=user_data.name,namekey=keyname,datekey=keydob,profilepicturekey=keypicture,beforeupdate=0,data=user_data,key=session["superuser"])

@app.route("/update/",methods=["GET","POST"])
def before_update():
    req_user=user.query.filter(user.email==session["email"]).one()
    try:
        image = b64encode(req_user.profile_picture).decode("utf-8")
        na=0
    except:
        image=0
        na=1
    user_data=user.query.filter(user.email==session["email"]).one()
    return render_template("6update.html",tkey=0, na=na,beforeupdate=1, username=user_data.name,im=image,data=user_data,key=session["superuser"])


@app.route("/updated/", methods=["GET","POST"])
def updated():
    req_user=user.query.filter(user.email==session["email"]).one()
    try:
        uploaded_image=request.files["image"]
        req_user.profile_picture=uploaded_image.read()
    except:
        pass
    try:
        name=request.form["name"]
        req_user.name=name
    except:
        pass
    try:
        dob=request.form["dob"]
        req_user.dob=dob
    except:
        pass
    db.session.commit()
    updated_user=user.query.filter(user.email==session["email"]).one()
    name=updated_user.name
    image = b64encode(updated_user.profile_picture).decode("utf-8")
    return render_template("7updated.html",tkey=0, username=updated_user.name,akey=0, data=updated_user, im=image, key=session["superuser"])

@app.route("/Account/", methods=["GET","POST"])
def account():
    data=user.query.filter(user.email==session["email"]).one()
    try:
        image = b64encode(data.profile_picture).decode("utf-8")
        na=0
    except:
        image=0
        na=1
    return render_template("7updated.html",tkey=1,username=data.name,akey=1,na=na, data=data,im=image,key=session["superuser"])

@app.route("/Contact/", methods=["GET","POST"])
def contact():
    return render_template("9Contact.html",msg=0,username=session["name"],Name=session["name"],key=session["superuser"],mail=session["email"])

@app.route("/Contact/send", methods=["GET","POST"])
def contact_send():
    emailing().contactadmin(session["email"],session["name"],request.form["subject"],request.form["message"])
    return render_template("9Contact.html",msg=1,username=session["name"],Name=session["name"],key=session["superuser"],mail=session["email"])

@app.route("/forgot_password", methods=["GET"])
def forgot_password_get():
    return render_template("forgot_password.html", key=0)

@app.route("/registered", methods=["POST"])
def registered():
    new_email=session["temp_email"]
    new_name=request.form["name"]
    new_dob=request.form["birthday"]
    new_password=request.form["password"]
    cnf_password=request.form["confirm_password"]
    chk=checking()
    if cnf_password==new_password:
        obj=updations().user_registration(name=new_name,email=new_email,bday=new_dob,pwd=new_password)
        session.clear()
        return render_template("message_prompt.html", message=new_name+" you have registered successfully")
    else:
        return render_template("password_doesnt_match.html")



@app.route("/forgot_password/reset_link/", methods=["GET","POST"])
def forgot_password_post():
    email_id=request.form["forgot_mail_id"]
    session["forgot_mail"]=email_id 
    a=emailing().forgot_password(email_id)
    if a==1:
        session.clear()
        return render_template("message_prompt.html",message="The email that you have entered is not registered with our database.\n Thank you.")
    return render_template("forgot_password.html",key=1,mail=email_id,msg=0)

@app.route("/forgot_password/verify", methods=["GET","POST"])
def forgot_verify():
    pwd=request.form["verification_code"]
    a=checking().isnotuser(session["forgot_mail"],pwd)
    if a[0]:
        return redirect("/forgot_password/set_new_password")
    else:
        return render_template("forgot_password.html", key=1,mail=session["forgot_mail"], msg=1)


@app.route("/forgot_password/set_new_password", methods=["GET","POST"])
def set_new_password():
    mail=session["forgot_mail"]
    return render_template("forgot_password.html",key=2,mail=mail,msg=0)

@app.route("/forgot_password/check_new_password", methods=["GET","POST"])
def check_new_password():
    pwd=request.form["password"]
    cnf_pwd=request.form["confirm_password"]
    #print(pwd,cnf_pwd)
    if pwd!=cnf_pwd:
        return render_template("forgot_password.html",key=2,mail=session["forgot_mail"],msg=1)
    else:
        name=updations().update_password(session["forgot_mail"],pwd)
        session.clear()
        return render_template("message_prompt.html",message="Dear "+name+" , The password is updated, try to login again with the new password.")
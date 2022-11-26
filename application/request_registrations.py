from urllib import request
from requests import delete

from application.book_registrations import book_registrations
from application.list_operations import make_2blobs
from .models import book_transactions,books,cart,history,fines, user
from .database import db 
import sqlalchemy
from base64 import b64encode
from sqlalchemy import delete
from datetime import datetime,timedelta
import pytz

class time_calc:
    def time(self):
        UTC = pytz.utc
        IST = pytz.timezone('Asia/Kolkata')
        datetime_ist = datetime.now(IST)
        return datetime_ist.strftime('%Y:%m:%d %H:%M:%S %Z')
    def time_with(self,start,end):
        difference=end-start
        return (difference.seconds)/60,difference.days
    def due_time(self,start,end,time=0,time_m=1,fc=0):
        #print("Actual sanctioned date: ", start)
        start_date=datetime.strptime(start, '%Y:%m:%d %H:%M:%S %Z')
        #print("Return request accepted date: ",end)
        end_date=datetime.strptime(end, '%Y:%m:%d %H:%M:%S %Z')
        expected_date=start_date+timedelta(days=time,hours=time,minutes=time_m,seconds=time)
        #print("Expected time to give book: ",expected_date)
        if expected_date>end_date:
            return 0
        else:
            return time_calc().time_with(expected_date,end_date)

class fine_operations:
    def calc_fine(self,transaction_id,pdf=5):
        start_tr=db.session.execute("SELECT date_time from book_transactions where state=1 and transaction_id=:id",{"id":transaction_id})
        for i in start_tr:
            s_date=i[0]
        #print(s_date,"date from database")
        end_tr=db.session.execute("SELECT date_time from book_transactions where state=3 and transaction_id=:id",{"id":transaction_id})
        for i in end_tr:
            e_date=i[0]
        #print(e_date,"end date from database")
        a=time_calc().due_time(s_date,e_date)
        #print(a[0])
        if a!=0:
            amount=a[1]*pdf 
            fine=fines(transaction_id=transaction_id,due=a[1],fine_amount=amount)
            db.session.add(fine)
            db.session.commit()
        else:
            return
    
    def student_fines(self,user_id):
        #fines.query.filter(fines.transaction_id==9).delete()
        db.session.commit()
        tr=db.session.execute("SELECT f.transaction_id,h.book_isbn, f.due, f.fine_amount from fines f,history h where h.transaction_id=f.transaction_id and h.book_user=:id group by f.transaction_id",{"id":user_id})
        data=[1]
        temp=[]
        for i in tr:
            temp+=[[i[0],i[1],i[2],i[3]]]
        #print(tuple(tr))
        if len(temp)==0:
            data[0]=0
        data+=[temp]
        return data 
    
    def all_fines(self):
        tr=db.session.execute("SELECT f.transaction_id,h.book_user,h.book_isbn, f.due, f.fine_amount from fines f,history h where h.transaction_id=f.transaction_id group by f.transaction_id")
        data=[1]
        temp=[]
        for i in tr:
            temp+=[[i[0],i[1],i[2],i[3],i[4]]]
        #print(tuple(tr))
        if len(temp)==0:
            data[0]=0
        data+=[temp]
        return data 



class request_operations:
    def generate_book_isbn(self,book_id):
        book=books.query.filter(books.book_id==book_id,books.available==1).first()
        return book.book_isbn

    # It will register a request for book
    # Reuest state should be 1
    # State should be 0

    def register_a_request(self,user_id,book_id):
        book_isbn=request_operations.generate_book_isbn(self,book_id)
        next_id_tr=db.session.execute('SELECT MAX(transaction_id) as id FROM book_transactions')
        next_id_h=db.session.execute('SELECT MAX(transaction_id) as id FROM history')
        for i in next_id_tr:
            if i.id is None:
                tr_id=0
                break
            else:
                tr_id=i.id
        for j in next_id_h:
            if j.id is None:
                h_id=0
                break
            else:
                h_id=j.id
        if h_id>tr_id:
            transaction_id=h_id
        else:
            transaction_id=tr_id
        transaction_id+=1
        cart_book=cart.query.filter(cart.user_email==user_id,cart.book_id==book_id).one()
        cart_book.cart_state=1
        db.session.commit()
        new_request=book_transactions(transaction_id=transaction_id, book_id=book_id, book_isbn=book_isbn, book_user=user_id, date_time=time_calc().time(), state=0,request_state=1)
        db.session.add(new_request)
        db.session.commit()
        book=books.query.filter(books.book_isbn==book_isbn, books.available==1).first()
        book.available=0
        db.session.commit()
        serial=book_transactions.query.filter(book_transactions.transaction_id==transaction_id).one()
        serial_id=serial.serial_no
        db.session.commit()
        return 
    
    #The Staff will accept the request 
    #Will make request state of previous transaction to 0
    #Add new transaction to the transaction table with state 1
    def accept_book_request(self,serial_no):
        tr=book_transactions.query.filter(book_transactions.serial_no==serial_no).one()
        tr.request_state=0
        db.session.commit()
        isbn=tr.book_isbn
        cart_book=cart.query.filter(cart.user_email==tr.book_user,cart.book_id==tr.book_id).one()
        cart_book.cart_state=2
        db.session.commit()
        request_accepted=book_transactions(transaction_id=tr.transaction_id, book_id=tr.book_id, book_isbn=tr.book_isbn, book_user=tr.book_user, date_time=time_calc().time(), state=1,request_state=0)
        db.session.add(request_accepted)
        db.session.commit()
        return 

    #Student can make a return request
    #Add a new transaction to the transaction table with state 2
    #and request_state=1
    def make_a_return_request(self,serial_no):
        tr=book_transactions.query.filter(book_transactions.serial_no==serial_no).one()
        tr.request_state=1
        db.session.commit()
        cart_book=cart.query.filter(cart.user_email==tr.book_user,cart.book_id==tr.book_id).one()
        cart_book.cart_state=3
        db.session.commit()
        r_request_make=book_transactions(transaction_id=tr.transaction_id, book_id=tr.book_id, book_isbn=tr.book_isbn, book_user=tr.book_user, date_time=time_calc().time(), state=2,request_state=1)
        #r_request_make=book_transactions(transaction_id=tr.transaction_id, book_id=tr.book_id, book_isbn=tr.book_isbn, book_user=tr.book_user, date_time="2022:09:22 00:11:57 IST", state=2,request_state=1)
        db.session.add(r_request_make)
        db.session.commit()
        return 
    
    #Staff will accept the request done by student
    #Making the request state of as 0
    #Adding the transaction to the transaction table with state=3 and request state as 0
    #Make the book available
    def accept_return_request(self,serial_no):
        tr=book_transactions.query.filter(book_transactions.serial_no==serial_no).one()
        tr.request_state=0
        isbn=tr.book_isbn
        cart_book=cart.query.filter(cart.user_email==tr.book_user,cart.book_id==tr.book_id).one()
        cart_book.cart_state=4
        db.session.commit()
        accept_request=book_transactions(transaction_id=tr.transaction_id, book_id=tr.book_id, book_isbn=tr.book_isbn, book_user=tr.book_user, date_time=time_calc().time(), state=3,request_state=0)
#        accept_request=book_transactions(transaction_id=tr.transaction_id, book_id=tr.book_id, book_isbn=tr.book_isbn, book_user=tr.book_user, date_time="2022:09:22 00:11:57 IST", state=3,request_state=0)
        db.session.add(accept_request)
        db.session.commit()
        book=books.query.filter(books.book_isbn==isbn).one()
        book.available=1
        db.session.commit()
        transactions=db.session.execute('Select serial_no,transaction_id,book_id,book_isbn,book_user,date_time,state from book_transactions where book_user=:user and book_isbn=:isbn',{'user':tr.book_user,'isbn':tr.book_isbn})
        ts=tuple(transactions)
        history_transactions().enter_history(ts)
        fine_operations().calc_fine(tr.transaction_id)
        book=book_transactions.query.filter(book_transactions.transaction_id==tr.transaction_id).delete()
        db.session.commit()
        return


class history_transactions:
    def history_retrieve(self,t):
        data=[1]
        temp=[]
        for i in t:
            temp+=[[i[0],i[1],b64encode(i[2]).decode("utf-8"),i[3]]]
        if len(temp)==0:
            data[0]=0
        temp=make_2blobs(temp)
        data+=[temp]
        return data 


    def enter_history(self,t):
        for i in t:
            add_history=history(serial_no=i[0],transaction_id=i[1],book_id=i[2],book_isbn=i[3],book_user=i[4],date_time=i[5],state=i[6])
            db.session.add(add_history)
            db.session.commit()
        return
    
    def history(self,email):
        his=db.session.execute("SELECT h.transaction_id,h.book_isbn,b.picture,b.book_name from history h,books b where h.book_isbn=b.book_isbn and h.book_user=:email group by h.transaction_id order by transaction_id DESC",{'email':email})
        return history_transactions().history_retrieve(his)

    def clear_history(self):
        hy=history.query.delete()
        db.session.commit()
        return


class student_request:

    def retrieve_data(self,t,a=0):
        data=[1]
        temp=[]
        for i in t:
            temp+=[[i[0],i[1],i[2],i[3],i[4], b64encode(i[5]).decode("utf-8"),i[6],i[7],i[8],i[9],i[10]]]
        if len(temp)==0:
            data[0]=0
        data+=[len(temp)]
        temp=make_2blobs(temp)
        data+=[temp]
        data+=[a]
        return data

    def retrieve_status_data(self,t):
        data=[1]
        temp=[]
        for i in t:
            temp+=[[i[0],i[1],i[2],b64encode(i[3]).decode("utf-8"),i[4]]]
        if len(temp)==0:
            data[0]=0
        temp=make_2blobs(temp)
        data+=[temp]
        return data 

    #Book Requests for staff (State should be 0 and request_state should be 1)
    def all_book_requests(self):
        request=db.session.execute('SELECT bt.book_id,bt.book_isbn,b.book_name,b.authors,b.edition,b.picture,bt.book_user,bt.state,bt.date_time,bt.transaction_id,bt.serial_no from book_transactions bt,books b where bt.request_state=1 and bt.state=0 and bt.book_isbn=b.book_isbn')
        return student_request().retrieve_data(request,0)

    #Return Requests for staff (State should be 2 and request_state should be 1)
    def all_return_requests(self):
        request=db.session.execute('SELECT bt.book_id,bt.book_isbn,b.book_name,b.authors,b.edition,b.picture,bt.book_user,bt.state,bt.date_time,bt.transaction_id,bt.serial_no from book_transactions bt,books b where bt.request_state=1 and bt.state=2 and bt.book_isbn=b.book_isbn')
        return student_request().retrieve_data(request,1)

    #All Requests for books by students (State should be 0 and Request state should be 1)
    def book_requests_of_student(self,email):
        request=db.session.execute('SELECT bt.book_id,bt.book_isbn,b.book_name,b.authors,b.edition,b.picture,bt.book_user,bt.state,bt.date_time,bt.transaction_id,bt.serial_no from book_transactions bt,books b where bt.book_user=:user and bt.request_state=1 and bt.state=0 and bt.book_isbn=b.book_isbn',{'user':email})
        return student_request().retrieve_data(request)

    #All Return Requests by students (State should be 2 and Request state should be 1)
    def student_return_requests(self,email):
        request=db.session.execute('SELECT bt.book_id,bt.book_isbn,b.book_name,b.authors,b.edition,b.picture,bt.book_user,bt.state,bt.date_time,bt.transaction_id,bt.serial_no from book_transactions bt,books b where bt.book_user=:user and bt.request_state=1 and bt.state=2 and bt.book_isbn=b.book_isbn',{'user':email})
        return student_request().retrieve_data(request)

    #All books that are currently with the student ( State should be 1 and request_state=0)
    def student_books_taken(self,email):
        request=db.session.execute('SELECT bt.book_id,bt.book_isbn,b.book_name,b.authors,b.edition,b.picture,bt.book_user,bt.state,bt.date_time,bt.transaction_id,bt.serial_no from book_transactions bt,books b where bt.book_user=:user and bt.state=1 and request_state=0 and bt.book_isbn=b.book_isbn',{'user':email})
        return student_request().retrieve_data(request)

    #Statuses of all the books that are involved by the user
    def student_book_status(self,email):
        status=db.session.execute('SELECT bt.transaction_id,bt.book_isbn,b.book_name,b.picture,MAX(bt.state) from book_transactions bt, books b where b.book_isbn=bt.book_isbn and bt.book_user=:email group by transaction_id',{"email":email})
        return student_request().retrieve_status_data(status)

    #This will return the book information and the Transaction details in the book_transactions
    def status_information(self,tr_id):
        trs=db.session.execute("SELECT book_isbn,state,date_time from book_transactions where transaction_id=:id ",{"id":tr_id})
        data=[]
        for i in trs:
            book_isbn=i[0]
            data+=[[i[1],i[2]]]
        #print(book_isbn)
        book_data=db.session.execute("SELECT book_id,book_name,book_isbn,authors,edition,picture from books where book_isbn=:isbn",{"isbn":book_isbn})
        data_book=[tr_id]
        for i in book_data:
            data_book+=[[i[0],i[1],i[2],i[3],i[4],b64encode(i[5]).decode("utf-8")]]
        data_book+=[data]
        return data_book

    #This will return the book information and the Transaction details in the history
    def history_information(self,tr_id):
        trs=db.session.execute("SELECT book_isbn,state,date_time from history where transaction_id=:id",{"id":tr_id})
        data=[]
        for i in trs:
            book_isbn=i[0]
            data+=[[i[1],i[2]]]
        book_data=db.session.execute("SELECT book_id,book_name,book_isbn,authors,edition,picture from books where book_isbn=:isbn",{"isbn":book_isbn})
        data_book=[tr_id]
        for i in book_data:
            data_book+=[[i[0],i[1],i[2],i[3],i[4],b64encode(i[5]).decode("utf-8")]]
        data_book+=[data]
        return data_book


    def delete_transaction(self):
        book_transactions.query.filter(book_transactions.transaction_id==10).delete()
        db.session.commit()
        return

    #Clears all the Transactions
    def clear_transactions(self):
        book_transactions.query.delete()
        db.session.commit()
        db.session.execute('update books set available=1')
        db.session.commit()
        return
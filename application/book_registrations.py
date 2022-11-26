from requests import delete
from .nophoto import images
from application.list_operations import make_2blobs
from .models import books,cart,user
from .database import db 
import sqlalchemy
from base64 import b64encode


class retrieve_data:
    def retrieve_with_isbn(self,a):
        data=[]
        for i in a:
            data+=[[i.book_id,i.book_name,i.authors,i.book_edition, b64encode(i.picture).decode("utf-8"),i.available,i.book_isbn]]
        data=make_2blobs(data)
        return data

    def retrieve_while_register(self,id):
        book_data=db.session.execute('SELECT book_id,book_name,authors,edition,picture,available,MAX(book_isbn),Min(book_isbn) from books where book_id=:id',{'id':id})
        data=[]
        for i in book_data:
            data=[i[0],i[1],i[2],i[3], b64encode(i[4]).decode("utf-8"),i[5],i[7],i[6]]
        return data
    def retrieve_with_object(self,t):
        data=[]
        for i in t:
            data+=[[i[0],i[1],i[2],i[3],i[4]]]
        pass

class book_queries(retrieve_data):
    def query_execute(self,input):
        a=db.session.execute(input)
        db.session.commit()
        return tuple(a)
        

class book_registrations:
    def generate_new_id(self):
        next_id=db.session.execute('SELECT MAX(book_id) as id FROM books')
        for i in next_id:
            if i.id is None:
                book_id=0
                break
            else:
                book_id=i.id
        book_id+=1
        return book_id
    def isavailable(self,name,edition):
        try:
            check_book=books.query.filter(books.book_name==name, books.edition==edition,books.available==1).one()
            return False
        except sqlalchemy.exc.NoResultFound:
            return True
        except:
            return False

    def register_book(self,name,author,copies,edition,picture):
        book_id=book_registrations().generate_new_id()
        if str(picture)=="b''":
            picture=images().nodp()
        for i in range(int(copies)):
            new_book=books(book_name=name,authors=author,edition=edition,picture=picture,book_id=book_id)
            db.session.add(new_book)
            db.session.commit()
        t=retrieve_data().retrieve_while_register(book_id)
        return t
    def make_no_available(self,key,t):
        if t==0:
            db.session.execute("update books set available=0 where book_isbn=:key",{"key":key})
            db.session.commit()
            data=db.session.execute("select book_id,book_isbn, book_name,authors,edition,picture,available from books where book_isbn=:key",{"key":key})
            data=tuple(data)
            temp=[data[0],data[1],data[2],data[3],data[4],b64encode(data[5]).decode("utf-8"),data[6]]
        else:
            db.session.execute("update books set available=0 where book_id=:key",{"key":key})
            db.session.commit()
            data=db.session.execute("select book_id,count(*), book_name,authors,edition,picture,available from books where book_id=:key group by book_id",{"key":key})
            data=tuple(data)
            temp=[data[0],data[1],data[2],data[3],data[4],b64encode(data[5]).decode("utf-8"),data[6]]
        return temp

class cart_oprations:
    def ids_from_isbns(self,isbn):
        book=db.session.execute('Select book_id from books where book_isbn=:isbn',{'isbn':isbn})
        isbns=[]
        for i in book:
            isbns+=[i[0]]
        return isbns

    def cart_books(self,email):
        book=db.session.execute('select b.book_id from books b, cart c where b.book_isbn=c.book_isbn')
        data=[]
        for i in book:
            data+=[i[0]]


class book_search:
    def retreive_data(self,t):
        data=[1,book_search().total_available()]
        temp=[]
        for i in t:
            temp+=[[i[0],i[1],i[2],i[3], b64encode(i[4]).decode("utf-8"),i[5]]]
        if len(temp)==0:
            data[0]=0
        data+=[len(temp)]
        temp=make_2blobs(temp)
        data+=[temp]
        return data

    def total_available(self):
        book=books.query.all()
        return len(book)

    def total_available_books(self):
        t=db.session.execute('SELECT book_id,book_name,authors,edition,COUNT(*) FROM books WHERE available=1 GROUP BY book_name,authors,edition').all()
        return book_search().retreive_data(t)
    
    def search_by_name(self,pattern):
        a='SELECT book_id,book_name,authors,edition,picture,COUNT(*) FROM books WHERE book_name LIKE '+"'%"+pattern+"%'"+' GROUP BY book_id'
        t=db.session.execute(a).all()
        return book_search().retreive_data(t)

    def search_by_author(self,pattern):
        l=[]
        count=0
        try:
            book=books.query.group_by(books.book_name,books.edition).all()
            Total_count=len(book)
            for i in book:
                if pattern in i.authors:
                    l+=[i]
                    count+=1
            return l,count,Total_count
        except:
            return False,False,False
        
    def search_by_isbn(self,isbn):
        l=[]
        try:
            book=books.query.filter(books.book_isbn==int(isbn)).all()
            Total_count=len(book)
            for i in book:
                l+=[i]
            return l,len(book),Total_count
        except:
            return False,False,False
    
    def search(self,option=0,pattern=""):
        option=int(option)
        if option==0:
            return book_search().search_by_name(pattern)
        elif option==1:
            return book_search().search_by_author(pattern)
        else:
            return book_search().search_by_isbn(pattern)
        

class student:
    def data_retrieve_for_student(self,data,books):
        data=[1]
        temp=[]
        for i in books:
            temp+=[[i[0],i[1],i[2],i[3], b64encode(i[4]).decode("utf-8"),i[5],i[6],i[7]]]
        temp=make_2blobs(temp)
        if len(temp)==0:
            data[0]=0
        data+=[temp]
        return data
    
    def data_retrieve_for_student_t(self,data,books,newdata,state_data):
        data=[1]
        temp=[]
        for i in books:
            if i[0] in newdata:
                #print(state_data[i[0]])
                temp+=[[i[0],i[1],i[2],i[3], b64encode(i[4]).decode("utf-8"),i[5],i[6],i[7],state_data[i[0]] ]]
            else:
                temp+=[[i[0],i[1],i[2],i[3], b64encode(i[4]).decode("utf-8"),i[5],i[6],i[7],-1 ]]
        temp=make_2blobs(temp)
        if len(temp)==0:
            data[0]=0
        data+=[temp]
        return data
    

    def Take_a_book(self,email):
        total=db.session.execute('SELECT COUNT(*) FROM books WHERE available=1 GROUP BY available').all()
        if len(total)==0:
            return False
        else:
            books_in_cart=db.session.execute('SELECT book_id from cart where user_email=:email',{'email':email})
            data=[]
            
            for i in books_in_cart:
                data+=[i[0]]
            
            if len(data)==0:
                book=db.session.execute('SELECT book_id,book_name,authors,edition,picture,COUNT(*),count(case when available=1 then 1 end) as ones,count(case when available=0 then 1 end) as zeros FROM books GROUP BY book_id').all()
            else:
                if len(data)==1:
                    data+=[-1]
                data=tuple(data)
                book=db.session.execute('SELECT book_id,book_name,authors,edition,picture,COUNT(*),count(case when available=1 then 1 end) as ones,count(case when available=0 then 1 end) as zeros FROM books WHERE book_id NOT IN {0} GROUP BY book_id'.format(data))
            return student().data_retrieve_for_student(data,book)
        
    def cart_books(self,email):
        books=db.session.execute('SELECT book_id from cart where user_email=:email',{'email':email})
        id_data=[]
        #print("Hello",books)
        for i in books:
            id_data+=[i[0]]
        #print(id_data)
        temp=[1]
        if len(id_data)==0:
            temp[0]=0
            return temp
        else:
            if len(id_data)==1:
                id_data+=[-1]
            data=tuple(id_data) 
            book=db.session.execute('select b.book_id,b.book_name,b.authors,b.edition,b.picture,count(*) as Total,count(case when b.available=1 then 1 end) as ones,count(case when b.available=0 then 1 end) as zeros,c.cart_state from books b,cart c where c.user_email=:mail and b.book_id=c.book_id and b.book_id in {0} GROUP by b.book_id'.format(data),{"mail":email}).all()
            book_data=[]
            #print(tuple(book),"Hello")
            for i in book:
                book_data+=[[i[0],i[1],i[2],i[3], b64encode(i[4]).decode("utf-8"),i[5],i[6],i[7],i[8]]]
            book_data=make_2blobs(book_data)
            return temp+[book_data]




    def add_to_cart(self,email,id):
        c=cart(book_id=id,user_email=email,cart_state=0)
        db.session.add(c)
        db.session.commit()
        return 



class book_deletion:

    def delete_a_book(self,book_id):
        book_id=int(book_id)
        sample=books.query.filter(books.book_id==book_id).first()
        count_book=books.query.filter(books.book_id==book_id).all()
        length=len(count_book)
        data=[sample.book_id,sample.book_name,sample.authors,sample.edition,b64encode(sample.picture).decode("utf-8"),length]
        count_book=books.query.filter(books.book_id==book_id).delete()
        db.session.commit()
        return data
    
    def delete_all(self):
        book=books.query.delete()
        cart=db.session.execute('delete from cart where book_id>0')
        db.session.commit()
        return

    def delete_a_cart_book(self,email,book_id):
        book=cart.query.filter(cart.user_email==email,cart.book_id==book_id).delete()
        db.session.commit()
        return

    def clear_cart(self):
        cart_books=cart.query.delete()
        db.session.commit()
        return


def make_3blobs(l):
    temp=[]
    k=[]
    k+=[l[0]]
    for i in range(1,len(l)):
        if i%3!=0:
            k+=[l[i]]
        else:
            temp+=[k]
            k=[l[i]]
    return temp+[k]

def make_2blobs(l):
    k=[]
    for i in range(len(l)):
        if i==0:
            temp=[]
        if i%2==0 and i!=0:
            k+=[temp]
            temp=[]
            temp+=[l[i]]
        else:
            temp+=[l[i]]
    if len(l)!=0:
        k=k+[temp]
    return k

def list_converter(s):
    print(s)
    b=s.split("%")
    return b[0],int(b[1]),b[2]
    
def listing_books(d):
    lis=[]
    for i in d.keys():
        temp=i.split("%")
        temp+=[d[i]]
        lis+=[temp]
    return lis

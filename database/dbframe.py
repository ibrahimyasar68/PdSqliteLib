import pandas as pd
import matplotlib.pyplot as plt
import sqlite3


baglantı= sqlite3.connect("C:\\Database\\DBL_Kayit.db")
dfbook=pd.read_sql_query("SELECT * FROM kayitlistesi",baglantı)
dfuser=pd.read_sql_query("SELECT * FROM users",baglantı)
dfwork=pd.read_sql_query("SELECT * FROM follow where status='out'",baglantı)





######################
###  Book Table   ####
######################

def df_count_items():
    sayi=len(dfbook['Id'])
    return sayi

def df_all_list():
    snc=[]
    for i in range(df_count_items()):
        snc.append((dfbook.iloc[i]).values)
    return snc    

def df_sort_list(sort):
    snc=list(dfbook[sort].unique())
    snc.sort()
    return snc

def df_srt_fltr(sort,name):
    sayi=(len(dfbook.query(f"{sort}=='{name}'")))
    snc=dfbook.query(f"{sort}=='{name}'")
    sn=[]
    for i in range(sayi):
        sn.append(([*(snc.iloc[i])]))
    return sayi,sn

def df_find_by_sort(sort,name):   
    sayi=len(dfbook.query(f"{sort}=='{name}'"))
    if sayi<1:        
        kyt=[]
        return sayi,kyt
    else:
        snc=dfbook.query(f"{sort}=='{name}'")
        kyt=([*snc.iloc[0]])
        return sayi,kyt

def rapor(sor,cnt): ###İstatistik için####
    snc=dfbook.groupby(sor)['Yili'].count().sort_values().tail(cnt)[::-1]   
    return snc


def piegraf():
    liste=rapor('Turu',15)
    names=liste.index[::]
    val=liste.values[::]
    valint=list(float(i) for i in val)    
    myexplode=[]
    for i in range(15):
        myexplode.append(0.05)  
    figure=plt.figure()
    axes=figure.add_axes([0,0,1,1])
    axes.pie(valint,labels=names, shadow=True, explode=myexplode, autopct="%1.1f%%")
    plt.show()

######################
###  User Table   ####
######################

def df_user_list(key):
    snc=list(dfuser[key])
    return snc


def df_user_find(name):   
    snc=dfuser.query(f"adi_soyadi=='{name}'")
    kyt=([*snc.iloc[0]])
    return kyt

######################
###  Work Table   ####
######################

## Kitap verme işlemlerinde kullanıcı listesi
def df_work_user_list():
    persid=list(dfwork['userId'].unique())
    liste=[]
    for per in persid:
        snc=dfuser.query(f"id=={per}")
        kyt=([*snc.iloc[0]])
        liste.append(kyt[3])
    liste.sort()
    return liste


## kitap verme işlemlerinde kitap listesi
def df_work_book_list():
    bks=list(dfwork['bookId'].unique())
    liste=[]
    for bk in bks:
        snc=dfbook.query(f"Id=={bk}")
        kyt=([*snc.iloc[0]])
        liste.append(kyt[1])
    liste.sort()
    return(liste)
  
## Kitap vermede kullanıcıya göre kitap listesi
def df_work_perbook(id):
    bks=dfwork.query(f"userId=='{id}'")['bookId'] 
    liste=[]
    for bk in bks:
        snc=dfbook.query(f"Id=={bk}")
        kyt=([*snc.iloc[0]])
        liste.append(kyt[1])
    liste.sort()
    return liste

def df_work_table_book():
    bks=dfwork[['bookId','userId','outdate']]
    kayit=[]
    for a,b,c in bks.values:
        book=((dfbook.query(f"Id=={a}")).iloc[0].values)        
        user=((dfuser.query(f"id=={b}")).iloc[0].values)   
    
        kayit.append([(book)[1],(book)[2],(book)[4],(user)[3],(user)[4],(user)[5],c])
    return (kayit)


if __name__ == "__main__":

    # piegraf()

    # x=piegraf()
    # x.show()


    pass
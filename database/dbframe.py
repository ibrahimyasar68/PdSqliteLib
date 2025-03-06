import pandas as pd
import matplotlib.pyplot as plt
import sqlite3


baglantı= sqlite3.connect("C:\\Database\\DBL_Kayit.db")
dfbook=pd.read_sql_query("SELECT * FROM kayitlistesi",baglantı)
dfuser=pd.read_sql_query("SELECT * FROM users",baglantı)




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

def df_user_list():
    snc=list(dfuser["kullanici"])
    return snc


def df_passw_list():
    snc=list(dfuser["sifre"])
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
    # axes.plot(valint,valint,label='Square')
    axes.pie(valint,labels=names, shadow=True, explode=myexplode, autopct="%1.1f%%")

    # plt.pie(valint,labels=names, shadow=True, explode=myexplode, autopct="%1.2f%%")
    # # return plt
    # plt.legend(title="Kitap Türleri",loc=2)
    plt.show()


if __name__ == "__main__":

    piegraf()

    # x=piegraf()
    # x.show()


    pass
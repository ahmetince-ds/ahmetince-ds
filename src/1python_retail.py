import pandas as pd 
import numpy as np
import seaborn as sns 
import matplotlib.pyplot as plt
import datetime as dt 
from sklearn.preprocessing import MinMaxScaler
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions



pd.set_option('display.max_columns',None)
pd.set_option('display.max_rows',None)
pd.set_option('display.float_format', lambda x:'%.5f' % x)


df = pd.read_excel('C:\\Users\Win10\Desktop\\rretail\CLTV_Prediction\\online_retail_II.xlsx')
df = df.copy()

print(df.head())
df['Description'].nunique()
df['Description'].value_counts()
df.groupby('Description').agg({'Quantity':'sum'})
df.groupby('Description').agg({'Quantity':'sum'}).sort_values('Quantity',ascending = False)
# Quantity ye göre azalan şekilde sıralama


# dosya uzantılı okutmalarda ' \\ ' işaretleri 2 kez kullanılır yol bilgisi verilir...
# pip install pandas openpyxl bu şekilde excel okumayı aktif edip .xlsx uzantılı dosyaları okuturuz...
# python.exe -m pip install --upgrade pips

df['Invoice'].nunique()
df['TotalPrice'] = df['Quantity'] * df['Price']
df.groupby('Invoice').agg({'TotalPrice':'sum'}).head()

#-----------------------------------------------------------------------------------------------------
# VERİYİ HAZIRLAMA
df.shape
df.isnull().sum()
df.dropna(inplace=True) # değerler düşürüldü...

df = df[~df['Invoice'].astype(str).str.contains('C', na=False)]


#------------------------------------------------------------------------------------------------------------------------------------
# RFM METRİKLERİNİN HESAPLANMASI

df['InvoiceDate'].max() # son tarihe gider
today_date = dt.datetime.now()

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days ,# recency
                                      'Invoice': lambda num:num.nunique(),# frequency
                                      'TotalPrice': lambda TotalPrice:TotalPrice.sum()}) # monetary


rfm.columns = ['recency', 'frequency', 'monetary'] 
rfm.describe().T
rfm = rfm[rfm['monetary'] > 0]

#---------------------------------------------------------------------------------------------------------------------------------
# RFM SKORLARININ HESAPLANMASI

rfm['recency_score'] = pd.qcut(rfm['recency'],5,labels=[5,4,3,2,1])
# iyi olan 5, kötü olan 1

rfm['monetary_score'] = pd.qcut(rfm['monetary'],5,labels=[1,2,3,4,5])

rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method='first'),5,labels=[1,2,3,4,5])

rfm['RFM_SCORE'] =(rfm['recency_score'].astype(str) +
                   rfm['frequency_score'].astype(str)) # string ifadeye çevrildi ve yan yana toplandı


rfm[rfm['RFM_SCORE'] == '55']
rfm[rfm['RFM_SCORE'] == '11']

#print(rfm[rfm['RFM_SCORE'] == '55'])
#print(rfm[rfm['RFM_SCORE'] == '11'])

#------------------------------------------------------------------------------------------------------------------------------
# RFM SEGMENTLERİNİN OLUŞTURULMASI

seg_map = {r'[1-2][1-2]': 'hipernating',
           r'[1-2][3-4]': 'at_risk',
           r'[1-2]5': 'cant_loose',
           r'3[1-2]': 'about_to_sleep',
           r'33': 'need_attention',
           r'[3-4][4-5]': 'loyal_customer',
           r'41': 'promissing',
           r'51': 'new_customers',
           r'[4-5][2-3]': 'potantial_loyallist',
           r'5[4-5]': 'champions' 
           }

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map,regex=True) # birleştirilen skorlar
rfm[['segment','recency','frequency','monetary']].groupby('segment').agg(['mean','count'])

rfm[rfm['segment'] == 'need_attention'].head()
rfm[rfm['segment'] == 'cant_loose'].index

new_df = pd.DataFrame()
new_df['new_customer_ID'] = rfm[rfm['segment'] == 'new_customers'].index
new_df['new_customer_ID'] = new_df['new_customer_ID'].astype(int)

new_df.to_csv('new_customers.csv')
rfm.to_csv('rfm.csv')

#---------------------------------------------------------------------------------------------------------

# tüm süreçlerin FONKSİYONLAŞTIRILMASI

def create_rfm(dataframe, csv=False):

    df = dataframe.copy()

    df.dropna(inplace=True)

    # 🔥 KRİTİK SATIR
    df['Invoice'] = df['Invoice'].astype(str)

    df = df[~df['Invoice'].str.contains('C', na=False)]
    df = df[df['Quantity'] > 0]
    df = df[df['Price'] > 0]

    df['TotalPrice'] = df['Quantity'] * df['Price']
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    today_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

    rfm = df.groupby('Customer ID').agg({
        'InvoiceDate': lambda date: (today_date - date.max()).days,
        'Invoice': 'nunique',
        'TotalPrice': 'sum'
    })

    rfm.columns = ['recency', 'frequency', 'monetary']

    if csv:
        rfm.to_csv("rfm.csv")

    return rfm


df = df.copy()
rfm_new = create_rfm(df,csv=True)

# CLTV VERİ HAZIRLAMA

df_ = pd.read_excel('C:\\Users\Win10\Desktop\\rretail\CLTV_Prediction\\online_retail_II.xlsx')

df = df_.copy()

df.isnull().sum()
df = df[ ~ df['Invoice'].astype(str).str.contains('C',na=False)]
df.dropna(inplace=True)
df['TotalPrice'] = df['Quantity'] * df['Price']
cltv_c = df.groupby('Customer ID').agg({'Invoice': lambda x:x.nunique(),
                                       'Quantity': lambda x:x.sum(),
                                       'TotalPrice': lambda x:x.sum()})

cltv_c.columns = ['total_transaction','total_unit','total_price']

# ORTALAMA SİPARİŞ DEĞERİ 
# formül => average_order_value = totalprice / total_transaction

cltv_c['average_order_value'] = cltv_c['total_price'] / cltv_c['total_transaction']

# SAYIN ALMA SIKLIĞI
# formül => purchase_frequency = total_transaction / total_number of customers
cltv_c['Purchase_frequency'] = cltv_c['total_transaction'] / cltv_c.shape[0]

# TEKRARLAMA VE KAYBETME ORANI
# FORMÜL => repeat rate & churn rate = (birden fazla alışveriş yapan müşteri sayısı / tüm müşteri)
repeat_rate = cltv_c[cltv_c['total_transaction'] > 1].shape[0] / cltv_c.shape[0]
churn_rate = 1 - repeat_rate
# KAR MARJI 
# FORMÜL =>   profit_margin = total_price * 0.10 # dipnot kar marjının oranını şirketler belirler

cltv_c['profit_margin'] = cltv_c['total_price'] * 0.10

# MÜŞTERİ DEĞERİ
# formül =>     customer_value = average_order_value * purchase_frequency
cltv_c['customer_value'] = cltv_c['average_order_value'] * cltv_c['Purchase_frequency']

# MÜŞTERİ YAŞAM BOYU DEĞERİ
# FORMÜL =>     customer_lifetime_value = (customer_value / churh_rate) * profit_margin

cltv_c['cltv'] = (cltv_c['customer_value'] / churn_rate) * cltv_c['profit_margin']

cltv_c.sort_values(by='cltv',ascending=False).head()

# SEGMENTLERİN OLUŞTURULMASI
cltv_c.sort_values(by='cltv',ascending=False).tail()

cltv_c['segment'] = pd.qcut(cltv_c['cltv'],4,labels=['D','C','B','A'])
cltv_c.sort_values(by='cltv',ascending=False).head()

cltv_c.groupby('segment').agg({'count','mean','sum'})
cltv_c.to_csv('cltv_c.csv')

# TÜM İŞLMELERİN FONKSİYONLAŞTIRILMASI

def create_cltv_c(dataframe,profit=0.10):
    # veriyi hazırlama
    dataframe = dataframe[ ~ dataframe['Invoice'].astype(str).str.contains('C',na=False)]
    dataframe = dataframe[(dataframe['Quantity'] > 0)]
    dataframe.dropna(inplace=True)
    dataframe['TotalPrice'] = dataframe['Quantity'] * dataframe['Price']
    cltv_c = dataframe.groupby('CustomerID').agg({'Invoice': lambda x:x.nunique(),
                                                   'Quantity': lambda x:x.sum(),
                                                   'TotalPrice': lambda x: x.sum()})
    
    cltv_c.columns = ['total_transaction','total_unit','total_price']
    # average_order_value
    cltv_c['average_order_value'] = cltv_c['total_price'] / cltv_c['total_transaction']
    # purchase_frequency
    cltv_c['purchase_frequency'] = cltv_c['total_transaction'] / cltv_c.shape[0]
    # repeat_rate & churn_rate
    repeat_rate = cltv_c[cltv_c.total_transaction > 1].shape[0] / cltv_c.shape[0]
    churn_rate = 1- repeat_rate
    # profit_margin
    cltv_c['profit_margin'] = cltv_c['total_price'] * profit
    # customer_value
    cltv_c['customer_value'] = (cltv_c['average_order_value'] * cltv_c['purchase_frequency'])
    # customer lifetime value
    cltv_c['cltv'] = (cltv_c['customer_value'] / churn_rate) * cltv_c['profit_margin']
    # segment
    cltv_c['segment'] = pd.qcut(cltv_c['cltv'],4,labels=['D','C','B','A'])
    
    if csv:
        cltv_c.to_csv("cltv_c.csv")
    return cltv_c

#-------------------------------------------------------------------------------------------------------------
# MÜŞTERİ YAŞAM BOYU DEĞERİ TAHMİNİ

def outlier_thresholds(dataframe,variable):
    quartile1 = dataframe[variable].quantile(0.01) # (0,25)
    quartile3 = dataframe[variable].quantile(0.99) #(0,75)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range      # bu fonksiyon kendisine girilen değişkenin eşik değerini hesaplar
    low_limit = quartile1 - 1.5 * interquantile_range

    return low_limit , up_limit


def replace_with_thresholds(dataframe,variable):
    low_limit ,up_limit = outlier_thresholds(dataframe , variable)
    dataframe.loc[(dataframe[variable] < low_limit),variable] = low_limit # alt limiti hesaplar
    dataframe.loc[(dataframe[variable] > up_limit),variable] = up_limit # üst limit


# verilerin okunması

df_ = pd.read_excel('C:\\Users\Win10\Desktop\\rretail\CLTV_Prediction\\online_retail_II.xlsx',sheet_name='Year 2010-2011')

# veri ön işleme
df.isnull().sum()
df.dropna(inplace=True)
df = df[~df['Invoice'].astype(str).str.contains('C', na=False)]

df = df[df['Quantity'] > 0 ]
df = df[df['Price'] > 0 ]

replace_with_thresholds(df,'Quantity')
replace_with_thresholds(df,'Price')

df['TotalPrice'] = df['Quantity'] * df['Price']
today_date = dt.datetime(2011,12,11)

# LİFETİME VERİ YAPISININ HAZIRLANMASI
# RECENCY = son satın alma üzerinden geçen zaman haftalık (müşteri bazlı)
# T = müşterinin yaşı ( haftalık , analiz tarihinden ne kadar önce ilk satın alma yapılmış)
# FREQUENCY = tekrar eden toplam satın alma sayısı
# MONETARY = satın alma başına ortalama kazanç

cltv_df = df.groupby('Customer ID').agg({'InvoiceDate' : [lambda date: (date.max() - date.min()).days,
                                                         lambda date: (today_date - date.min()).days],
                                        'Invoice': lambda num: num.nunique(),
                                        'TotalPrice': lambda TotalPrice: TotalPrice.sum()})


cltv_df.columns = cltv_df.columns.droplevel(0)
cltv_df.columns = ['recency','T','frequency','monetary']
cltv_df['monetary'] = cltv_df['monetary'] / cltv_df['frequency']
cltv_df.describe().T
cltv_df = cltv_df[(cltv_df['frequency'] > 1)] # satın alma sıklığı
cltv_df['recency'] = cltv_df['recency'] / 7
cltv_df['T'] = cltv_df['T'] / 7       # son iki satır haftalık hesap yapar

#------------------------------------------------------------------------------------------------------------
# BG- NBD MODELİNN KURULMASI

bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(cltv_df['frequency'],
        cltv_df['recency'],
        cltv_df['T'])

# 1 haftalık ilk 10 müşteri
bgf.conditional_expected_number_of_purchases_up_to_time(1,cltv_df['frequency'],
                                                          cltv_df['recency'],
                                                          cltv_df['T']).sort_values(ascending=False).head(10)
# 1 ay için tahmin etme
bgf.predict(4,cltv_df['frequency'],
             cltv_df['recency'],
            cltv_df['T']).sort_values(ascending=False).head(10)

cltv_df['expected_purc_1_month'] = bgf.predict(4,cltv_df['frequency'],
                                            cltv_df['recency'],
                                            cltv_df['T'])


# 3 aylık
cltv_df['expected_purc_3_month'] = bgf.predict(4*3,cltv_df['frequency'],
                                            cltv_df['recency'],
                                            cltv_df['T'])


#--------------------------------------------------------------------------------------
# TAHMİN SONUÇLARININ DEĞERLENDİRİLMESİ
plot_period_transactions(bgf)
plt.show()


print(rfm_new.head())
print(cltv_df.head())

#---------------------------------------------------------------------------------------------------------------

# GAMMA GAMMA MODELİ KURULMASI

ggf = GammaGammaFitter(penalizer_coef=0.001)
ggf.fit(cltv_df['frequency'],cltv_df['monetary'])
ggf.conditional_expected_average_profit(cltv_df['frequency'],cltv_df['monetary']).sort_values(ascending=False).head()
cltv_df['expected_average_profit'] = ggf.conditional_expected_average_profit(cltv_df['frequency'],cltv_df['monetary'])
cltv_df.sort_values('expected_average_profit',ascending=False).head(10)

cltv = ggf.customer_lifetime_value(bgf,cltv_df['frequency'],cltv_df['recency'],cltv_df['T'],cltv_df['monetary'], ##### buradan itibaren düzenle
                                        time=3,freq='W',discount_rate=0.01)

cltv.head()
cltv = cltv.reset_index()
cltv_final = cltv_df.merge(cltv,on='Customer ID',how='left')
cltv_final.sort_values(by='clv',ascending=False).head()

#----------------------------------------------------------------------------------------------------------------
# CLTV'YE GÖRE SEGMENTLERİN OLUŞTURULMASI

cltv_final['segment'] = pd.qcut(cltv_final['clv'],4,labels=['D','C','B','A'])
cltv_final.sort_values(by='clv',ascending=False).head()
cltv_final.groupby('segment').agg({'count','mean','sum'})

#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------

# FONKSİYONLAŞTIRMA


def create_cltv_p(dataframe, month=3):

    df = dataframe.copy()

    # 🔹 kolonları normalize et
    df.columns = df.columns.str.replace(" ", "")

    # 🔹 veri ön işleme
    df.dropna(inplace=True)

    df['Invoice'] = df['Invoice'].astype(str)
    df = df[~df['Invoice'].str.contains('C', na=False)]

    df = df[(df['Quantity'] > 0)]
    df = df[(df['Price'] > 0)]

    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    replace_with_thresholds(df, 'Quantity')
    replace_with_thresholds(df, 'Price')

    df['TotalPrice'] = df['Quantity'] * df['Price']

    today_date = df['InvoiceDate'].max()

    # 🔹 CLTV dataframe
    cltv_df = df.groupby('CustomerID').agg({
        'InvoiceDate': [
            lambda x: (x.max() - x.min()).days,
            lambda x: (today_date - x.min()).days
        ],
        'Invoice': 'nunique',
        'TotalPrice': 'sum'
    })

    cltv_df.columns = cltv_df.columns.droplevel(0)
    cltv_df.columns = ['recency', 'T', 'frequency', 'monetary']

    cltv_df['monetary'] = cltv_df['monetary'] / cltv_df['frequency']

    cltv_df = cltv_df[cltv_df['frequency'] > 1]

    # haftalık
    cltv_df['recency'] = cltv_df['recency'] / 7
    cltv_df['T'] = cltv_df['T'] / 7

    # 🔹 BG-NBD
    bgf = BetaGeoFitter(penalizer_coef=0.001)
    bgf.fit(cltv_df['frequency'],
            cltv_df['recency'],
            cltv_df['T'])

    cltv_df['expected_purc_1_week'] = bgf.predict(
        1, cltv_df['frequency'], cltv_df['recency'], cltv_df['T']
    )

    cltv_df['expected_purc_1_month'] = bgf.predict(
        4, cltv_df['frequency'], cltv_df['recency'], cltv_df['T']
    )

    cltv_df['expected_purc_3_month'] = bgf.predict(
        12, cltv_df['frequency'], cltv_df['recency'], cltv_df['T']
    )

    # 🔹 Gamma-Gamma
    ggf = GammaGammaFitter(penalizer_coef=0.001)
    ggf.fit(cltv_df['frequency'], cltv_df['monetary'])

    cltv_df['expected_average_profit'] = ggf.conditional_expected_average_profit(
        cltv_df['frequency'], cltv_df['monetary']
    )

    # 🔹 CLTV
    cltv = ggf.customer_lifetime_value(
        bgf,
        cltv_df['frequency'],
        cltv_df['recency'],
        cltv_df['T'],
        cltv_df['monetary'],
        time=month,
        freq="W",
        discount_rate=0.01
    )

    cltv = cltv.reset_index()  # CustomerID + clv

    cltv_final = cltv_df.merge(cltv, on='CustomerID', how='left')

    # 🔹 segment
    cltv_final['segment'] = pd.qcut(cltv_final['clv'], 4, labels=['D','C','B','A'])

    return cltv_final


df = df_.copy()
cltv_final2 = create_cltv_p(df)
cltv_final2.to_csv('cltv_prediction.csv')

#>>>>>>>>>>>>>>>>>>

# >> GRAFİKLER

cltv_final['clv'].hist(bins=50)
plt.title("CLTV Distribution")
plt.show()


# RFM Segment Dağılımı
rfm['segment'].value_counts().plot(kind='bar')
plt.title("RFM Segment Distribution")
plt.show()

#  CLTV Dağılımı
sns.histplot(cltv_final['clv'], bins=50)
plt.title("CLTV Distribution")
plt.show()

# Top Customers
cltv_final.sort_values("clv", ascending=False).head(10).plot(
    x="Customer ID", y="clv", kind="bar"
)
plt.title("Top 10 Customers by CLTV")
plt.show()


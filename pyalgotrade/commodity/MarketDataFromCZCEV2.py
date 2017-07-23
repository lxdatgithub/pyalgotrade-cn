#!/usr/local/bin/python
# -*-coding:utf-8-*-
# Get market data from futures exchanges
# designed and programed by lianxiangbin(LianZhang,qq785674410)
# 2014-10-20

import urllib
from pyquery import PyQuery
import sqlite3
import datetime


class MarketDataFromCZCE:

    # define the attributes
    def __init__(self, date, save_url):
        self.date = date.replace("/", "-").strip()  # date[0:4]+date[5:7]+date[-2:]#"2014/10/15"
        self.url = r"http://www.czce.com.cn/cms/cmsface/czce/exchangefront/calendarnewquery.jsp"
        self.PostDic = {"commodity": "", "dataType": "DAILY", "pubDate": self.date}
        # print(self.PostDic)
        self.SaveUrl = save_url
        self.Data = {}

    # get the html page

    def get_web_page(self):
        post_dic_decoded = urllib.parse.urlencode(self.PostDic).encode(encoding='gbk')
        request_ = urllib.request.Request(self.url, post_dic_decoded)
        page_fetched = urllib.request.urlopen(request_).read().decode("gbk", "ignore")
        if not page_fetched:
            print("Dear Host,I can not find the web page")
        return page_fetched

    # this is the trading date
    def get_trading_day(self):
        trading_day = datetime.datetime(int(self.date[0:4]), int(self.date[5:7]), int(self.date[-2:]))
        return trading_day

    # Get the data we needed from the origin file
    def get_needed_data(self):
        my_page = self.get_web_page()
        trading_day = self.get_trading_day()
        contents = PyQuery(my_page)
        #print(contents)
        A = contents("table").eq(3)
        A = PyQuery(A)
        for tr in A("tr"):
            Contrasts=[]
            values=[trading_day]
            for i in range(len(tr)):
                data=PyQuery(tr).find("td").eq(i).text()
                if i==0:
                    Contrasts.append(data)
                    key=Contrasts[0]
                    Symbol=key[0:2]
                    values.append(Symbol)
                else:
                    values.append(data)
            
            
            if ("总计" in key) or ("小计" in key) or ("品种月份" in key):
                continue
            values[1:]=[element.replace(",","").replace("-","").strip() for element in values[1:]]
            self.Data.setdefault(key,values)
            
    #Insert into DB
    def insert_to_db(self):
        self.get_needed_data()
        conna=sqlite3.connect(self.SaveUrl)
        #if conna:
        #    print("database is successfully connected")
        cursor=conna.cursor()
        SQLquery1="create table if not exists CZCE(Contracts varchar(20),date datetime,Symbol varchar(20),PreSettlement numeric(15,2),Open numeric(15,2),\
                  High numeric(15,2),Low numeric(15,2),Close numeric(15,2),Settlement numeric(15,2),Change1 numeric(15,2),Change2 numeric(15,2),\
                  Volume numeric(25,2),OpenInt numeric(25,2),ChangeofOpenInt numeric(25,2),Turnover numeric(30,2),SettlementofDelivery numeric(15,2))"
        cursor.execute(SQLquery1)
        for key,value in self.Data.items():
            Iter=(key,value[0],value[1],value[2],value[3],value[4],value[5],value[6],value[7],value[8],value[9],value[10],value[11],value[12],value[13],value[14])
            #print(Iter)
            SQLquery2="insert into CZCE"+" "+"values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
            cursor.execute(SQLquery2,Iter)
        conna.commit()
        conna.close()
        
if __name__=="__main__":
    try:
        test=MarketDataFromCZCE("2014/10/15")
        test.insert_to_db()
    except Exception as e:
        print("something wrong")
        print(e)

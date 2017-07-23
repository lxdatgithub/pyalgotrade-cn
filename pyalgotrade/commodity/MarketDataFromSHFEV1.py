#!/usr/local/bin/python
#-*-coding:utf-8-*-
#Get market data from futures exchanges
#designed and programed by lianxiangbin(LianZhang,qq785674410)
#2014-10-21

import urllib.request
import urllib.parse
from pyquery import PyQuery
import sqlite3
import datetime

class MarketDataFromSHFE:


    #define the attributes
    def __init__(self,date,SaveUrl):
        self.date=date[0:4]+date[5:7]+date[-2:];#"2014/05/23->20140523"
        self.url="http://www.shfe.com.cn/data/dailydata/kx/kx"+self.date+".dat";
        self.Data={};
        self.SaveUrl=SaveUrl;
  
    #get the html page
    def GetWebPage(self):
        MyPage=urllib.request.urlopen(self.url).read();#.decode("utf-8")
        if not MyPage:
            print("Dear Host,I can not find the web page");
        return MyPage;

    #this is the trading date
    def GetTheTradingDay(self):
        TradingDay=datetime.datetime(int(self.date[0:4]),int(self.date[4:6]),int(self.date[-2:]));
        return TradingDay;

    #Get the data we needed from the origin file
    def GetNeededData(self):
        MyPage=self.GetWebPage();
        MyPage=eval(MyPage);
        TradingDay=self.GetTheTradingDay();
        #print(MyPage);
        for dic in MyPage["o_curinstrument"]:
            key=dic["PRODUCTID"].strip()+dic["DELIVERYMONTH"];
            if (u"商品名称" in key) or (u"小计" in key) or (u"总计" in key):
                continue;
            Symbol=dic["PRODUCTID"].strip();
            Symbol=Symbol[0:2];
            values=[TradingDay,Symbol,dic["PRODUCTNAME"],dic["PRESETTLEMENTPRICE"],dic["OPENPRICE"],dic["HIGHESTPRICE"],dic["LOWESTPRICE"],dic["CLOSEPRICE"],\
                    dic["SETTLEMENTPRICE"],dic["ZD1_CHG"],dic["ZD2_CHG"],dic["VOLUME"],dic["OPENINTEREST"],dic["OPENINTERESTCHG"]];
            self.Data.setdefault(key,values);

    #Insert into DB
    def InsertDataToDB(self):
        self.GetNeededData();
        conna=sqlite3.connect(self.SaveUrl);
        #if conna:
        #    print("database is successfully connected");
        cursor=conna.cursor();
        SQLquery1="create table if not exists SHFE(Contracts varchar(20),date datetime,Symbol varchar(10),productname nvarchar(30),PreSettlement numeric(15,2),\
                  Open numeric(15,2),High numeric(15,2),Low numeric(15,2),Close numeric(15,2),Settlement numeric(15,2),Change1 numeric(15,2),\
                  Change2 numeric(15,2),Volume numeric(25,2),OpenInt numeric(25,2),ChangeofOpenInt numeric(25,2))";
        cursor.execute(SQLquery1);
        for key,value in self.Data.items():
            Iter=(key,value[0],value[1],value[2],value[3],value[4],value[5],value[6],value[7],value[8],value[9],value[10],value[11],value[12],value[13]);
            #print(Iter);
            SQLquery2="insert into SHFE"+" "+"values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
            cursor.execute(SQLquery2,Iter);
        conna.commit();
        conna.close();

if __name__=="__main__":
    try:
        test=MarketDataFromSHFE("2014/10/15");
        MyPage=test.InsertDataToDB();
    except Exception as e:
        print("something wrong");
        print(e);

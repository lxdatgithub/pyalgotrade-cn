#!/usr/local/bin/python
#-*-coding:utf-8-*-
#Get market data from futures exchanges
#designed and programed by lianxiangbin(LianZhang,qq785674410)
#2014-10-16

import urllib.request
import re
import sqlite3
import datetime

class MarketDataFromCFFEX:
    
    #define the attributes
    def __init__(self,date,SaveUrl):
        self.date=date;#"2014/05/23"
        self.url="http://www.cffex.com.cn/fzjy/mrhq/"+self.date[0:4]+self.date[5:7]+"/"+self.date[-2:]+"/"+"index.xml";
        self.Data={};
        self.SaveUrl=SaveUrl;
    #get the html page
    def GetWebPage(self):
        MyPage=urllib.request.urlopen(self.url).read().decode("utf-8","ignore");
        if not MyPage:
            print("Dear Host,I can not find the web page");
        return MyPage;

    #Get the data we needed from the origin file
    def GetNeededData(self):
        MyPage=self.GetWebPage();
        #print(MyPage);
        Pattern=re.compile(r"<dailydata>(.*?)</dailydata>",re.DOTALL);
        Iterms=Pattern.findall(MyPage);
        if not Iterms:
            print("Get the page successfully!!");
        for Iterm in Iterms:
            Pattern=re.compile(r"<instrumentid>(.*?)</instrumentid>");
            Contracts=Pattern.findall(Iterm);
            Pattern=re.compile(r"<tradingday>(.*?)</tradingday>");
            TradingDay=Pattern.findall(Iterm);
            TradingDay=datetime.datetime(int(TradingDay[0][0:4]),int(TradingDay[0][4:6]),int(TradingDay[0][-2:]));
            Pattern=re.compile(r"<openprice>(.*?)</openprice>");
            Open=Pattern.findall(Iterm);
            if Open[0]=="":
                continue;
            Open=float(Open[0]);
            Pattern=re.compile(r"<highestprice>(.*?)</highestprice>");
            High=Pattern.findall(Iterm);
            High=float(High[0]);
            Pattern=re.compile(r"<lowestprice>(.*?)</lowestprice>");
            Low=Pattern.findall(Iterm);
            Low=float(Low[0]);
            Pattern=re.compile(r"<closeprice>(.*?)</closeprice>");
            Close=Pattern.findall(Iterm);
            Close=float(Close[0]);
            Pattern=re.compile(r"<openinterest>(.*?)</openinterest>");
            OpenInt=Pattern.findall(Iterm);
            OpenInt=float(OpenInt[0]);
            Pattern=re.compile(r"<settlementprice>(.*?)</settlementprice>");
            Settlement=Pattern.findall(Iterm);
            Settlement=float(Settlement[0]);
            Pattern=re.compile(r"<presettlementprice>(.*?)</presettlementprice>");
            PreSettlement=Pattern.findall(Iterm);
            PreSettlement=float(PreSettlement[0]);
            Pattern=re.compile(r"<volume>(.*?)</volume>");
            Volume=Pattern.findall(Iterm);
            Volume=float(Volume[0]);
            Pattern=re.compile(r"<turnover>(.*?)</turnover>");
            Turnover=Pattern.findall(Iterm);
            Turnover=float(Turnover[0]);
            key=str(Contracts[0]).strip();
            Symbol=key[0:2];
            #print(key);
            Values=[Symbol,TradingDay,Open,High,Low,Close,OpenInt,Settlement,PreSettlement,Volume,Turnover];
            #print(Values);
            self.Data.setdefault(key,Values);
            
    #Insert into DB
    def InsertDataToDB(self):
        self.GetNeededData();
        conna=sqlite3.connect(self.SaveUrl);
        #if conna:
        #    print("database is successfully connected");
        cursor=conna.cursor();
        SQLquery1="create table if not exists CFFEX(Contracts varchar(20),Symbol nvarchar(20),date datetime,Open numeric(15,2),High numeric(15,2),\
                  Low numeric(15,2),Close numeric(15,2),OpenInt numeric(25,2),Settlement numeric(15,2),PreSettlement numeric(15,2),\
                  Volume numeric(25,2),Turnover numeric(30,5))";     
        cursor.execute(SQLquery1);
        for key,value in self.Data.items():
            Iter=(key,value[0],value[1],value[2],value[3],value[4],value[5],value[6],value[7],value[8],value[9],value[10]);
            #print(Iter);
            SQLquery2="insert into CFFEX"+" "+"values(?,?,?,?,?,?,?,?,?,?,?,?)";
            cursor.execute(SQLquery2,Iter);
        conna.commit();
        conna.close();

if __name__=="__main__":
    try:
        test=MarketDataFromCFFEX("2014/10/15");
        MyPage=test.InsertDataToDB();
    except Exception as e:
        print(e);


		
		
		
		
		
		

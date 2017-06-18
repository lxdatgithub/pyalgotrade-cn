from pyalgotrade.feed import csvfeed

feed = csvfeed.Feed("Date", "%Y-%m-%d")
# feed.addValuesFromCSV("./data/quandl_gold_2.csv")
feed.addValuesFromCSV("/home/xdliu/workspace/open_source_tools/pyalgotrade-cn/samples/data/VEU-2007-yahoofinance.csv")
for dateTime, value in feed:
    print dateTime, value


from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
import os

from pyalgotrade import strategy
from pyalgotrade import plotter
from pyalgotrade.barfeed import sina_feed as sf

from pyalgotrade.stratanalyzer import sharpe

class MultiMACrossOver(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, short_ma_period, medium_ma_period, long_ma_period):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.__position = None
        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(False)
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__short_sma = ma.SMA(self.__prices, short_ma_period)
        self.__medium_sma = ma.SMA(self.__prices, medium_ma_period)
        self.__long_sma = ma.SMA(self.__prices, long_ma_period)


    def getShortSMA(self):
        return self.__short_sma

    def getLongSMA(self):
        return self.__long_sma

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # If a position was not opened, check if we should enter a long position.
        if self.__prices > self.__long_sma:
            # just long if price is above long sma
            if self.__position is None:
                if cross.cross_above(self.__short_sma, self.__medium_sma) > 0:
                    shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                    # Enter a buy market order. The order is good till canceled.
                    self.__position = self.enterLong(self.__instrument, shares, True)
            else:
                if not self.__position.exitActive() and cross.cross_below(self.__short_sma, self.__medium_sma) > 0:
                    self.__position.exitMarket()

        elif self.__prices < self.__long_sma:
            if self.__position is not None:
                if cross.cross_below(self.__short_sma, self.__medium_sma) > 0:
                    shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                    self.__position = self.enterShort(self.__instrument, shares, True)
            else:
                if not self.__position.exitActive() and cross.cross_above(self.__short_sma, self.__long_sma) > 0:
                    self.__position.exitMarket()





def main(plot):
    instrument = "FG0"
    short_ma_Period = 10
    medium_ma_period = 20
    long_ma_period = 99

    # Download the bars.
    # feed = yahoofinance.build_feed([instrument], 2011, 2012, ".")
    csv_path = os.path.abspath('../histdata/commodity') + '/' + instrument + '.csv'
    feed = sf.Feed()
    feed.addBarsFromCSV(instrument, csv_path)
    # feed = csvfeed.Feed('Date', )
    strat = MultiMACrossOver(feed, instrument, short_ma_period=short_ma_Period,
                             medium_ma_period=medium_ma_period, long_ma_period=long_ma_period)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)

    if plot:
        plt = plotter.StrategyPlotter(strat, True, True, True)
        plt.getInstrumentSubplot(instrument).addDataSeries("short sma", strat.getShortSMA())
        plt.getInstrumentSubplot(instrument).addDataSeries("long sma", strat.getLongSMA())

        # plt.getInstrumentSubplot(instrument).addDataSeries("middle", strat.getBollingerBands().getMiddleBand())
        # plt.getInstrumentSubplot(instrument).addDataSeries("lower", strat.getBollingerBands().getLowerBand())

    strat.run()
    print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05)
    if plot:
        plt.plot()
    pass


if __name__ == "__main__":
    main(True)

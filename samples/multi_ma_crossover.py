
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
import os

from pyalgotrade import strategy
from pyalgotrade import plotter
from pyalgotrade.barfeed import sina_feed as sf

from pyalgotrade.stratanalyzer import sharpe

class SMACrossOver(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.__position = None
        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(False)
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__sma = ma.SMA(self.__prices, smaPeriod)

    def getSMA(self):
        return self.__sma

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if cross.cross_above(self.__prices, self.__sma) > 0:
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                # Enter a buy market order. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, shares, True)
            elif cross.cross_below(self.__short_sma, self.__long_sma) > 0:
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                self.__position = self.enterShort(self.__instrument, shares, True)

        # Check if we have to exit the position.
        elif not self.__position.exitActive() and cross.cross_below(self.__prices, self.__sma) > 0:
            self.__position.exitMarket()


def main(plot):
    instrument = "FG0"
    sma_Period = 40

    # Download the bars.
    # feed = yahoofinance.build_feed([instrument], 2011, 2012, ".")
    csv_path = os.path.abspath('../histdata/commodity') + '/' + instrument + '.csv'
    feed = sf.Feed()
    feed.addBarsFromCSV(instrument, csv_path)
    # feed = csvfeed.Feed('Date', )
    strat = SMACrossOver(feed, instrument, sma_Period)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)

    if plot:
        plt = plotter.StrategyPlotter(strat, True, True, True)
        plt.getInstrumentSubplot(instrument).addDataSeries("sma", strat.getSMA())
        # plt.getInstrumentSubplot(instrument).addDataSeries("middle", strat.getBollingerBands().getMiddleBand())
        # plt.getInstrumentSubplot(instrument).addDataSeries("lower", strat.getBollingerBands().getLowerBand())

    strat.run()
    print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05)
    if plot:
        plt.plot()
    pass


if __name__ == "__main__":
    main(True)
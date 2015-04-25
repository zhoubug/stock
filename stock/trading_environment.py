from zipline.finance import trading
import calendar_cn
import pandas as pd

bm = '000001.SS'
trading.environment = trading.TradingEnvironment(bm_symbol=bm,
                                                 exchange_tz='Asia/Shanghai')
trading.environment.trading_days = calendar_cn.trading_days

trading.environment.open_and_closes = pd.DataFrame(
    index=trading.environment.trading_days,
    columns=["market_open","market_close"])
trading.environment.open_and_closes.market_open = (
    trading.environment.open_and_closes.index + pd.to_timedelta(60*9+30,unit="m")).to_pydatetime()
trading.environment.open_and_closes.market_close = (
    trading.environment.open_and_closes.index + pd.to_timedelta(60*15,unit="m")).to_pydatetime()

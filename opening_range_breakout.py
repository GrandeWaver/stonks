import sqlite3
import config
import alpaca_trade_api as tradeapi
from datetime import date

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT id FROM strategy WHERE name = 'opening_range_breakout'
""")

strategy_id = cursor.fetchone()['id']

cursor.execute("""
    SELECT symbol, name 
    FROM stock 
    JOIN stock_strategy 
    ON stock_strategy.stock_id = stock.id
    WHERE stock_strategy.strategy_id = ?
""", (strategy_id,))

stocks = cursor.fetchall()
symbols = [stock['symbol'] for stock in stocks]
print(symbols)

current_date = date.today().isoformat()

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)
orders = api.list_orders(status='all', limit=500, after=f"{current_date}T16:30:00Z")
existing_order_symbols = [order.symbol for order in orders]

start_minute_bar = f"{current_date} 14:20:00-05:00"  # should be 9:30:00-5:00 but we have missing data
end_minute_bar = f"{current_date} 14:35:00-05:00"  # should be 9:45:00-5:00 because alpaca free api sucks

for symbol in symbols:
    minute_bars = api.get_barset(symbol, timeframe='1Min',
                                 start=current_date,
                                 end=current_date).df

    opening_range_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    opening_range_bars = minute_bars.loc[opening_range_mask]

    opening_range_low = opening_range_bars[symbol]['low'].min()  # Delete [symbol] when use polygon.io
    opening_range_high = opening_range_bars[symbol]['high'].max()
    opening_range = opening_range_high - opening_range_low

    after_opening_range_mask = minute_bars.index >= end_minute_bar
    after_opening_range_bars = minute_bars.loc[after_opening_range_mask]

    after_opening_range_breakout = after_opening_range_bars[after_opening_range_bars[symbol]['close'] > opening_range_high]

    if not after_opening_range_breakout.empty:
        if symbol not in existing_order_symbols:
            limit_price = after_opening_range_breakout[symbol]['close'][0]
            print(f'placing order for {symbol} at {limit_price}, closed above {opening_range_high} at \n{after_opening_range_breakout[symbol].iloc[0]}')

            api.submit_order(
                symbol=symbol,
                side='buy',
                type='limit',
                qty='100',
                time_in_force='day',
                order_class='bracket',
                limit_price= limit_price,
                take_profit=dict(
                    limit_price=limit_price + opening_range,
                ),
                stop_loss=dict(
                    stop_price=limit_price - opening_range,
                )
            )
        else:
            print(f"Already an order for {symbol}, skipping")


""" Tip:
Establish your bias based on the daily chart’s price action. Trade in direction of the trend/supply-demand imbalance

Description:
A simple way to build a watchlist of stocks for this strategy every morning is to simply see which stocks have high 
relative volume and big price moves during pre-market. Then look at what is causing it: is it an earnings report, news, 
dilution, something else? Look at the stock’s news on your news feed, and look at their recent SEC filings. If you find 
nothing, it’s better to stay away because you can’t identify why a stock is moving.

More info about idea of opening_range_breakout:
https://www.warriortrading.com/opening-range-breakout/"""

import sqlite3
import config

connection = sqlite3.connect(config.DB_FILE)

cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_price_24
    (
        id INTEGER PRIMARY KEY,
        stock_id INTEGER,
        date NOT NULL,
        open NOT NULL,
        high NOT NULL,
        low NOT NULL,
        close NOT NULL,
        volume NOT NULL,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock 
    (
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        exchange TEXT NOT NULL
    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_price
    (
        id INTEGER PRIMARY KEY,
        stock_id INTEGER,
        date NOT NULL,
        open NOT NULL,
        high NOT NULL,
        low NOT NULL,
        close NOT NULL,
        volume NOT NULL,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS strategy (
    id INTEGER PRIMARY KEY,
    name NOT NULL,
    description TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_strategy (
    stock_id INTEGER NOT NULL,
    strategy_id INTEGER NOT NULL,
    FOREIGN KEY (stock_id) REFERENCES stock (id)
    FOREIGN KEY (strategy_id) REFERENCES strategy (id)
    UNIQUE(stock_id,strategy_id)
    )
""")


'''
strategies = ['opening_range_breakout', 'opening_range_breakdown']
descriptions = ['opening_range_breakout is good for bullish stocks', 'opening_range_breakdown is good for bear stocks']

for strategy, description in zip(strategies, descriptions):
    cursor.execute("""
    INSERT INTO strategy (name, description) VALUES (?, ?)
    """, (strategy, description,))

connection.commit()
'''
import config
import sqlite3

import json


def search(value: str):
    value = f'{value}%'

    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM (
        SELECT symbol, name
        FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
        GROUP BY stock_id
        ORDER BY avg(volume) desc)
        where name like (?)
        limit 5
    """, (value, ))

    results = cursor.fetchall()
    '''dictionary = list(results)'''
    return results


'''symbol = [f"/stock/{i['symbol']}" for i in search("q")]

for i in symbol:
    print(i)'''



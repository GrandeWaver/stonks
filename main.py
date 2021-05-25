import config
import sqlite3
import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/zplayground")
def zplayground(request: Request):
    return templates.TemplateResponse("zplayground.html", {"request": request})


def search(value: str):
    value = f'%{value}%'

    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM (
        SELECT "/stocks/" || symbol as [symbol], name
        FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
        GROUP BY stock_id
        ORDER BY avg(volume) desc)
        where name like (?)
        limit 10
    """, (value, ))

    rows = cursor.fetchall()
    dictionary = list(rows)
    return dictionary


@app.get("/data")
def data_search(request: Request):
    q = request.query_params.get('q', False)
    search_bar = search(q)
    if q == "40M1N":
        return {'search': [{"name": "40M1N", "symbol": "http://google.com?q=No co cwaniaku?"}]}
    else:
        return {'search': search_bar}


@app.get("/data/prices")
def data_prices():
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
                SELECT open as price, name, symbol
                FROM stock_price_24 JOIN stock ON stock.id = stock_price_24.stock_id
                ORDER BY symbol asc
                LIMIT 50
            """)
    prices = cursor.fetchall()
    return {'prices': prices}


@app.get("/")
def index(request: Request):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT stock.name as stock_name, strategy.name as strategy_name
        FROM stock, strategy, stock_strategy 
        WHERE stock_strategy.stock_id = stock.id
        AND stock_strategy.strategy_id = strategy.id
        ORDER BY 1,2
    """)
    rows = cursor.fetchall()

    return templates.TemplateResponse("index.html", {"request": request, "rows": rows, })


@app.get("/stocks/")
def stocks(request: Request):
    stock_filter = request.query_params.get('filter', False)

    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if stock_filter == 'new_closing_highs':
        cursor.execute("""
        SELECT * FROM (
        SELECT symbol, name, stock_id, max(close), date, close as price
        FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
        GROUP BY stock_id
        ORDER BY symbol
        ) WHERE date = (SELECT max(date) FROM stock_price)
        """)
    elif stock_filter == 'new_closing_lows':
        cursor.execute("""
        SELECT * FROM (
        SELECT symbol, name, stock_id, min(close), date, close as price
        FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
        GROUP BY stock_id
        ORDER BY symbol
        ) WHERE date = (SELECT max(date) FROM stock_price)
        """)
    else:
        cursor.execute("""
        SELECT * FROM (
        SELECT stock_id, close as price, symbol, name
        FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
        WHERE date = (SELECT max(date) FROM stock_price)
        GROUP BY stock_id
        ORDER BY symbol asc)
        LIMIT 50
        """)

    rows = cursor.fetchall()

    return templates.TemplateResponse("stocks.html", {"request": request, "stocks": rows})


@app.get("/strategies/")
def strategies(request: Request,):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM strategy
    """)

    strategies = cursor.fetchall()

    return templates.TemplateResponse("strategies.html", {"request": request, "strategies": strategies})


@app.get("/stocks/{symbol}")
def stock_detail(request: Request, symbol):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM strategy
    """)

    strategies = cursor.fetchall()

    cursor.execute("""
        SELECT id, symbol, name FROM stock WHERE symbol = ?
    """, (symbol,))

    row = cursor.fetchone()

    cursor.execute("""
        SELECT * FROM stock_price WHERE stock_id = ? ORDER BY date desc
    """, (row['id'],))

    prices = cursor.fetchall()
    return templates.TemplateResponse("stock_detail.html",
                                      {"request": request, "stock": row, "bars": prices, "strategies": strategies})


@app.post("/apply_strategy")
def apply_strategy(strategy_id: int = Form(...), stock_id: int = Form(...)):
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
           INSERT INTO stock_strategy (stock_id, strategy_id) VALUES (?, ?)
       """, (stock_id, strategy_id))

    connection.commit()

    return RedirectResponse(url=f"/strategies/{strategy_id}", status_code=303)


@app.get("/strategies/{strategy_id}")
def strategy(request: Request, strategy_id):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, description
        FROM strategy
        WHERE id = ?
    """, (strategy_id,))

    strategy = cursor.fetchone()

    cursor.execute("""
        SELECT symbol, name
        FROM stock INNER JOIN stock_strategy 
        ON stock_strategy.stock_id = stock.id
        WHERE strategy_id = ?
    """, (strategy_id,))

    stocks = cursor.fetchall()

    return templates.TemplateResponse("strategy_detail.html", {"request": request, "stocks": stocks, "strategy": strategy})

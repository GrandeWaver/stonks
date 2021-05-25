import config
import sqlite3

connection = sqlite3.connect(config.DB_FILE)

cursor = connection.cursor()

cursor.execute("""
    DROP TABLE stock_price
""")

print("Dropped stock_price table.")

connection.commit()
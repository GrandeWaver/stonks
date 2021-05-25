@ECHO OFF
ECHO Populate stocks and prices
ECHO Please Wait...
ECHO ============================
@CALL "C:\Users\macha\anaconda3\Scripts\activate.bat"
ECHO ============================

ECHO Python drop_db.py.py
ECHO ============================
python C:\Users\macha\Desktop\Make" "Me" "Rich\v4\drop_db.py
ECHO ============================
ECHO End
ECHO ============================

ECHO Python create_db.py.py
ECHO ============================
python C:\Users\macha\Desktop\Make" "Me" "Rich\v4\create_db.py
ECHO ============================
ECHO End
ECHO ============================

ECHO Python populate_stocks.py
ECHO ============================
python C:\Users\macha\Desktop\Make" "Me" "Rich\v4\populate_stocks.py
ECHO ============================
ECHO End

ECHO Python populate_prices.py
ECHO ============================
python C:\Users\macha\Desktop\Make" "Me" "Rich\v4\populate_prices.py
ECHO ============================
ECHO End
ECHO ============================

PAUSE
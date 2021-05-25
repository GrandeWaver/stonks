set root=C:\Users\macha\anaconda3
call %root%\Scripts\activate.bat %root%
call uvicorn main:app --reload
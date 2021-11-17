from urllib import request
import requests
import json
from fastapi import FastAPI, Request, Depends, Form, File, UploadFile
from fastapi import templating
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, session
from starlette.responses import RedirectResponse
from database import SessionLocal, engine
import models
from pydantic import BaseModel
from models import *
import pandas as pd
from sqlalchemy import text
from urllib.request import urlopen
app = FastAPI()
models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")
# for input data


class StockRequest(BaseModel):
    symbol: str


class Register_class(BaseModel):
    Name: str
    email: str
    password: str


class login_class(BaseModel):
    email: str
    password: str


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get('/registration')
async def read_root(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})
    return {"Hello": "World"}


@app.post('/registration_form')
async def validate_registartion_crendentail(request: Request, db: Session = Depends(get_db), name: str = Form(...),  email: str = Form(...), password: str = Form(...)):
    create_user = Register()  # model

    create_user.Name = name
    create_user.email = email
    create_user.password = password
    try:
        db.add(create_user)
        db.commit()

    except:
        return templates.TemplateResponse("registration.html", {"request": request, })

    return templates.TemplateResponse("login.html", {"request": request})


@app.post('/register')
def register(regist: Register_class, db: Session = Depends(get_db)):
    create_user = Register()  # model

    create_user.Name = regist.Name
    create_user.email = regist.email
    create_user.password = regist.password
    try:
        db.add(create_user)
        db.commit()

    except:

        return {
            "code": "Error (Email Must be not Used before)",
            "message": "User not created"
        }
    return {
        "code": "Success!!!!",
        "message": "User created"
    }


@app.post('/login_form')
async def validate_login_credintial(request: Request, email: str = Form(...), password: str = Form(...), db:session=Depends(get_db)):
    
        query = 'select * from Users where email ='+"'" + str(email)+"'"+' and password ='+"'"+str(password)+"'"
        db_email = ''
        db_password = ''
        qu_df = engine.connect().execute(text(query))
        print('DF :: ', qu_df)
        for x in qu_df:
            db_name = x['Name']
            db_email = x['email']
            db_password = x['password']
        print('db_email :: ', db_email)
        print('db_password :: ', db_password)
        if email == db_email and password == db_password :
            file = open('crentendial.txt', 'w')
            file.write(email)
            file.close()
            incl = db.query(models.user_stock).filter(models.user_stock.user_email == 'notapplied@yet.com2')
            return RedirectResponse('/home')
        else:
            return templates.TemplateResponse("login.html", {"request": request})


@app.get('/')
async def read_root(request: Request):
    file = open('crentendial.txt' )
    logined_email = file.read()
    file.close()
    if len(logined_email) != 0 :
        return RedirectResponse('/home')
    return templates.TemplateResponse("login.html", {"request": request})


@app.post('/login')
def login(login: login_class, db: Session = Depends(get_db)):
    email = login.email
    password = login.password
    db_email = ''
    db_password = ''
    query = 'select * from Users where email =' + "'" + \
        str(email)+"'"+' and password ='+"'"+str(password)+"'"
    print("QUERY :: ", query)
    qu_df = engine.connect().execute(text(query))
    print('DF :: ', qu_df)
    for x in qu_df:
        print(x)
        db_name = x['Name']
        db_email = x['email']
        db_password = x['password']
    print('db_name ::', db_name)
    print('db_email :: ', db_email)
    print('db_password :: ', db_password)

    if email == db_email and password == db_password:
        file = open('crentendial.txt', 'w')
        file.write(email)
        file.close()
        return{
            'code': 'Success!!!!',
            'message': 'Login Successfully',
        }

    return{
        'login': 'User Not Found',
        'message': 'Login Failed'
    }


@app.get('/createstock')
def demo(request:Request, db:Session = Depends(get_db)):
    file = open('crentendial.txt' )
    logined_email = file.read()
    file.close()
    stocks_already_added_list = []
    stocks_already_added = db.query(models.user_stock).filter(models.user_stock.user_email == logined_email).all()
    
    for x in stocks_already_added:
        stocks_already_added_list.append( str(x.symbol) )
        # print(x.symbol)
    # print('======================================================')
    link = "https://asx.api.markitdigital.com/asx-research/1.0/companies/directory?page=0&itemsPerPage=25&order=ascending&orderBy=companyName&includeFilterOptions=false&recentListingsOnly=false"
    response = urlopen(link)
    data_json = json.loads(response.read())
    symbols_list = []
    a = data_json['data']['items']
    for x in a:
        
        if stocks_already_added_list.__contains__( str(x['symbol']) ):
            print(x['symbol'],'    xxxxxxxxxx')
        else:
            symbols_list.append( str(x['symbol']) )
    print(symbols_list)
    print(stocks_already_added_list)

    return templates.TemplateResponse("add_stock.html", {"request": request, 'symb': symbols_list})


@app.post('/addstock')
def createStock(request:Request, symbol: str = Form(...), db: Session = Depends(get_db)):
    stock = user_stock() # model

    file = open('crentendial.txt' )
    logined_email = file.read()
    file.close()
    
    stock.user_email = logined_email
    stock.symbol = symbol
    try:
        db.add(stock)
        db.commit()
        db.refresh()
        # incl = db.query(models.user_stock).all()
    except:
        incl = db.query(models.user_stock).all()
    return RedirectResponse('/home')


@app.get('/home')
def home(request:Request,  db: Session = Depends(get_db)):
    file = open('crentendial.txt' )
    logined_email = file.read()
    file.close()

    link = "https://asx.api.markitdigital.com/asx-research/1.0/companies/directory?page=0&itemsPerPage=25&order=ascending&orderBy=companyName&includeFilterOptions=false&recentListingsOnly=false"
    response = urlopen(link)
    data_json = json.loads(response.read())
    a = data_json['data']['items']


    query = 'select * from user_stocks where user_email ='+"'" + str(logined_email)+"'"

    qu_df = engine.connect().execute(text(query))
    print('DF :: ', qu_df)
    symbol_list = []
    whole_list_co = []

    for x in qu_df:
        db_symbol = x['symbol']
        symbol_list.append(db_symbol)
        db_email = x['user_email']
        print(db_symbol, db_email , '       from get')
        print('')

        for y in a:
            if y['symbol'] == db_symbol:
                print(y)
                whole_list_co.append(y)
                break
         

    return templates.TemplateResponse("home.html", {"request": request, 'stocks': whole_list_co, 'email': logined_email })


@app.post('/home')
def home(request:Request,  db: Session = Depends(get_db)):
    file = open('crentendial.txt' )
    logined_email = file.read()
    file.close()

    link = "https://asx.api.markitdigital.com/asx-research/1.0/companies/directory?page=0&itemsPerPage=25&order=ascending&orderBy=companyName&includeFilterOptions=false&recentListingsOnly=false"
    response = urlopen(link)
    data_json = json.loads(response.read())
    a = data_json['data']['items']


    query = 'select * from user_stocks where user_email ='+"'" + str(logined_email)+"'"

    qu_df = engine.connect().execute(text(query))
    print('DF :: ', qu_df)
    symbol_list = []
    whole_list_co = []

    for x in qu_df:
        db_symbol = x['symbol']
        symbol_list.append(db_symbol)
        db_email = x['user_email']
        print(db_symbol, db_email , '       from get')
        print('')

        for y in a:
            if y['symbol'] == db_symbol:
                print(y)
                whole_list_co.append(y)
                break
         

    return templates.TemplateResponse("home.html", {"request": request, 'stocks': whole_list_co, 'email': logined_email })

@app.get('/logout')
def logout(request:Request):
    file = open('crentendial.txt', 'w')
    file.write('')
    file.close()

    return templates.TemplateResponse("login.html", {"request": request})

@app.get('/delete/{item}')
async def delete(item):

    file = open('crentendial.txt' )
    logined_email = file.read()
    file.close()

    # query = 'select * from user_stocks where user_email ='+"'" + str(logined_email)+"'"
    # DELETE FROM table_name WHERE condition;

    query = 'DELETE FROM user_stocks WHERE user_email ='+ "'" + str(logined_email)+"'" + ' and symbol = '+"'"+ str(item) +"'"
    qu_df = engine.connect().execute(text(query))
    # print('DF :: ', qu_df)
    return RedirectResponse('/home')
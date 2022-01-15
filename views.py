from django.http.response import JsonResponse
from django.shortcuts import render
from django.views import View
import pandas as pd
import numpy as np
import alpaca_trade_api as tradeapi
import json
import os
from dotenv import load_dotenv
from datetime import date
from datetime import datetime
from newsapi import NewsApiClient

# Create your views here.
class Index(View):
    def get(self, request):
        return render(request, "index.html",{})

class Dataview(View):
    def get(self, request):
        #obtain get variable of stock symbol from index.html
        PikTik= request.GET.get('stock')
        #obtain get variable of date/times from index.html
        Sdate = request.GET.get('span')
        
        date_today = date.today()
        date_5y= date_today- pd.DateOffset(years= 5) # "Y5"
        date_5y= date_5y.strftime('%Y-%m-%d')
        date_1y= date_today- pd.DateOffset(years= 1) #"Y1"
        date_1y= date_1y.strftime('%Y-%m-%d')
        date_YTD= date_today- pd.DateOffset(years= 5) #"YTD"
        date_YTD= date_YTD.strftime('%Y-%m-%d')
        date_6m = date_today- pd.DateOffset(months= 6) #"M6"
        date_6m= date_6m.strftime('%Y-%m-%d')
        date_1m = date_today- pd.DateOffset(months= 1) #"M1"
        date_1m= date_1m.strftime('%Y-%m-%d')

        z ={"Y5": date_5y,
            "Y1": date_1y,
            "YTD": date_YTD,
            "M6": date_6m,
            "M1": date_1m
            }

       

        #connect to api obtain TikTik data & return below
        #load Alpaca api
        alpaca_api_key = "PK55DVY40BM8OTB4HSVX"
        alpaca_secret_key = "VDBV4ac8Cu1MiLfxYgKSh7zJ1H7u4ifXXtKNylW6"

        api = tradeapi.REST(
            alpaca_api_key,
            alpaca_secret_key,
            api_version = "v2"
        )

        # Set timeframe to '1D'
        timeframe = "1D"

        # Set start and end datetimes between now and 3 years ago.
        #start_date = pd.Timestamp("2018-09-11", tz="America/New_York").isoformat()

        start_date = pd.Timestamp(z[Sdate], tz="America/New_York").isoformat()
        end_date = pd.Timestamp.today( tz="America/New_York").isoformat()

        # Set the ticker information
        tickers = [PikTik]

        # Get 3 year's worth of historical price data for Microsoft and Coca-Cola
        df_historical = api.get_barset(
            tickers,
            timeframe,
            start=start_date,
            end=end_date,
            limit=1000,
        ).df

        #Clean/drop all data except date and closing price
        df_historical.columns= df_historical.columns.droplevel()
        df_historical.drop(columns=['open', 'high', 'low', 'volume'], inplace=True)
        df_historical.index = df_historical.index.date

        


        jlist = df_historical.index.tolist()
        jlist= [datetime.combine(i, datetime.min.time())for i in jlist]
        jlist= [i.timestamp()*1000 for i in jlist]

        #Convert historical price data to a list
        slist = df_historical["close"].tolist()
        
        #combine list
        clist = list(zip(jlist, slist))
        clist = [list(i) for i in clist]


       #connected api > send to index.html  
        return JsonResponse({"price": clist}, status=200, safe= False)
        

#new class for news data

class Newsclass(View):
    def get(self, request):

        PikTik = request.GET.get('symbol')
        Getdatee = request.GET.get('date') 
        # ^^^^if Getdatee is pulled in milliseconds then divide by 1000
        Getdatee= int(Getdatee)
        Getdatee= Getdatee/1000
        
        #convert unix timestamp to Y-M-D 
        unix_conversion = datetime.fromtimestamp(Getdatee).strftime('%Y-%m-%d')

        #allow for 3 days before and after selected date to qur
        startdate=pd.to_datetime(unix_conversion) + pd.DateOffset(days=-3)
        startdate=startdate.strftime('%Y-%m-%d')
        enddate = pd.to_datetime(unix_conversion) + pd.DateOffset(days=3)
        enddate= enddate.strftime('%Y-%m-%d')

        newsapi_key = "a278db94e334403e98f13370130968ef" 
        newsapi = NewsApiClient(newsapi_key)

        stock_headlines = newsapi.get_everything(
        q = PikTik,  
        language="en",
        from_param= startdate,
        to=enddate,
         
        )

        cn = stock_headlines["articles"]
        newstitles_url=[]
        for i in range(len(cn)):
    #newstitles_url.append(cn[i]['title'])
            title=cn[i]['title']
            URLz= cn[i]['url']
            data= {}
            data["title"] =title
            data["url"] = URLz
            newstitles_url.append(data)




        return JsonResponse({"Snews": newstitles_url}, status=200, safe= False)

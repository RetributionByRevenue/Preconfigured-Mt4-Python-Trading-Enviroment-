import pandas as pd
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import numpy as np
import time
import datetime
import talib
import json
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails
import oandapyV20.endpoints.orders as orders
import oandapyV20
import oandapyV20.endpoints.positions as positions
while True:
 try:  
    #################DOWNLOAD CANDLES##########################
    #fx_pairs='USDCHFGBPUSDEURUSDUSDJPYUSDCADAUDUSDEURGBPEURAUDEURCHFEURJPYGBPCHFCADJPYGBPJPYAUDNZDAUDCADAUDCHFAUDJPYCHFJPYEURNZDEURCADCADCHFNZDJPYNZDUSD'
    fx_pairs='EURUSD'
    counter1=(len(fx_pairs)/6)
    api = oandapyV20.API(access_token='b1820d124857b58655e36eaa7f856b50-f9269344d4a6e789a9ce102df15af97d')
    pos = positions.OpenPositions(accountID='101-002-10197028-002')
    logs=str(api.request(pos))
    logs=logs.replace("'"," ")
    print(logs)
    while counter1>0:
        string=fx_pairs[-6:]
        print(string)
        fx_pairs=fx_pairs[0:-6]
        
    
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)
        client = oandapyV20.API(access_token='b1820d124857b58655e36eaa7f856b50-f9269344d4a6e789a9ce102df15af97d',
                                headers={"Accept-Datetime-Format":"Unix"})
        
        params = {
          "count": 1200,
          "granularity": "M5"
        }
        
        print ('Downloading ohlc data for '+string+'!')
        print('...')
    
        r = instruments.InstrumentsCandles(instrument=string[0:3]+'_'+string[3:6] , params=params)
        
        client.request(r)
        df=pd.DataFrame(r.response['candles'])
        #print(df)
        length=(len(df))-1
        low= np.asarray([])
        high= np.asarray([])
        close= np.asarray([])
        openn= np.asarray([])
        while length>0:
            specific_candle=pd.DataFrame(r.response['candles'][length])
            #print(specific_candle)
            obtain_low=specific_candle.tail(2)
            obtain_low=obtain_low.head(1)
            obtain_low=(obtain_low.mid.values)
            #print(obtain_low)
            obtain_close=specific_candle.head(1)
            obtain_close=obtain_close.mid.values
            obtain_high=specific_candle.head(2)
            obtain_high=obtain_high.tail(1)
            obtain_high=(obtain_high.mid.values)
            obtain_open=specific_candle.tail(1)
            obtain_open=obtain_open.mid.values
            #print(obtain_high)
            low=np.insert(low,0,float(obtain_low))
            high=np.insert(high,0,float(obtain_high))
            close=np.insert(close,0,float(obtain_close))
            openn=np.insert(openn,0,float(obtain_open))
            kopen= pd.DataFrame(columns=['open'], data=openn)
            khigh= pd.DataFrame(columns=['high'], data=high)
            klow=pd.DataFrame(columns=['low'], data=low)
            kclose=pd.DataFrame(columns=['close'], data=close)
            klines=pd.concat([kopen,khigh,klow,kclose,df], axis=1)
            
            length=length-1
        
        klines.mid=klines.mid.shift(-1)
        klines.complete=klines.complete.shift(-1)
        klines.time=klines.time.shift(-1)
        klines.volume=klines.volume.shift(-1)
        klines=klines.drop(columns=['mid'])
        klines.drop(klines.tail(1).index,inplace=True)
        print(klines.head(5))
        print(klines.tail(5))
        ####################### MATH ###########################
        MA_ARRAY_13=talib.EMA(np.array(klines.close), timeperiod=13)
        RSI_ARRAY_13=talib.RSI(MA_ARRAY_13, timeperiod=13)
        MA_RSI_OMA_21=talib.EMA(RSI_ARRAY_13, timeperiod=21)
        MA_RSI_OMA_144=talib.EMA(RSI_ARRAY_13, timeperiod=144)
        print(RSI_ARRAY_13[-10:])
        print(MA_RSI_OMA_21[-10:])
        print(MA_RSI_OMA_144[-10:])
        print('========================================')
        ##### Trade conditions###
        current_price=klines.tail(1)
        #print(klines.tail(1))
        current_price=current_price.close
        current_price=current_price.tolist()
        #print(current_price)
        current_price=current_price[-1]
        print('current price is ', current_price)
        if 'JPY' in string:
    
                rounding=3
                Long_SL=current_price-0.50
                Long_TP=current_price+0.20
                Short_SL=current_price+0.50
                Short_SL=current_price-0.20
        else:
                rounding=5
                Long_SL=current_price-0.0050
                Long_TP=current_price+0.0020
                Short_SL=current_price+0.0050
                Short_TP=current_price-0.0020
        
    
        print('=====================================')
        
        print('====================================')
        if string[0:3]+'_'+string[3:6] not in logs:
            if MA_RSI_OMA_21[-1] < 15:
                if MA_RSI_OMA_21[-1] > RSI_ARRAY_13[-1] and MA_RSI_OMA_144[-1] > RSI_ARRAY_13[-1]:
                    ''
                    api = oandapyV20.API(access_token='b1820d124857b58655e36eaa7f856b50-f9269344d4a6e789a9ce102df15af97d')
                    
                    mktOrder = MarketOrderRequest(
                        instrument=string[0:3]+'_'+string[3:6],
                        units=10000,
                        takeProfitOnFill=TakeProfitDetails(price=Long_TP).data,
                        stopLossOnFill=StopLossDetails(price=Long_SL).data)
                    r = orders.OrderCreate('101-002-10197028-002',data=mktOrder.data)
                    try:
                        rv = api.request(r)
                    except oandapyV20.exceptions.V20Error as err:
                        print(r.status_code, err)
                    else:
                        print(json.dumps(rv, indent=2))   
            elif MA_RSI_OMA_21[-1] > 85:
                if MA_RSI_OMA_21[-1] < RSI_ARRAY_13[-1] and MA_RSI_OMA_144[-1] < RSI_ARRAY_13[-1]:
                    ''
                    api = oandapyV20.API(access_token='b1820d124857b58655e36eaa7f856b50-f9269344d4a6e789a9ce102df15af97d')
                    
                    mktOrder = MarketOrderRequest(
                        instrument=str(string[0:3]+'_'+string[3:6]),
                        units=-10000,
                        takeProfitOnFill=TakeProfitDetails(price=Short_TP).data,
                        stopLossOnFill=StopLossDetails(price=Short_SL).data)
                    r = orders.OrderCreate('101-002-10197028-002',data=mktOrder.data)
                    try:
                        rv = api.request(r)
                    except oandapyV20.exceptions.V20Error as err:
                        print(r.status_code, err)
                    else:
                        print(json.dumps(rv, indent=2))
            else:
                print('not valid conditions to make trade')
        else:
            print('that particular pair is in trade')
        

 except Exception as e:
     #print('annoying error happened, :/ reloop anyways...')
     #print(str(e))
     print('Timestamp: {:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()))
     time.sleep(10)

'''
import json
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails
import oandapyV20.endpoints.orders as orders
import oandapyV20
import oandapyV20.endpoints.positions as positions
#from exampleauth import exampleAuth

STOP_LOSS = 1.12
TAKE_PROFIT = 1.0

api = oandapyV20.API(access_token='b1820d124857b58655e36eaa7f856b50-f9269344d4a6e789a9ce102df15af97d')

mktOrder = MarketOrderRequest(
    instrument="EUR_USD",
    units=-10000,
    takeProfitOnFill=TakeProfitDetails(price=TAKE_PROFIT).data,
    stopLossOnFill=StopLossDetails(price=STOP_LOSS).data)
r = orders.OrderCreate('101-002-10197028-002',data=mktOrder.data)
try:
    rv = api.request(r)
except oandapyV20.exceptions.V20Error as err:
    print(r.status_code, err)
else:
    print(json.dumps(rv, indent=2))        


pos = positions.OpenPositions(accountID='101-002-10197028-002')
logs=str(api.request(r))
logs=logs.replace("'"," ")

print(logs)
if "EUR_USD" in logs:
    print('true')        
'''
        
        
        
        
        
        
        
        
        
        
        
        
        
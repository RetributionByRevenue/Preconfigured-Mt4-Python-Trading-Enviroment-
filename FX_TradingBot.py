'''demonstration of a tradingbot that can place order to mt4, just need mt4 "Place_Order" expert advisor endabled
and dll imports & allowed live trading to be enabled on the mt4 client.

most forex brokers do not have a api and sadly we are stuck with mt4 to algo trade fx, at least this is a minor compermise
that can bring the power of python for trading profibility :)

this trading bot will produce a csv that an expert advisor can read and place orders from. the csv file is then deleted

made by @slay_the_normies
'''
import pandas as pd 
import csv
import time
import talib
import numpy as np
from pathlib import Path
path = str(Path(__file__).parent.absolute())
path=path.replace("\\","\\\\")
path=path[:path.find("Pythonic")]
logs=''#fetch oanda current open orders data with your own api key, convert data to string and check if the pair is inside string object
fx_pairs='''AUDJPY CADJPY CHFJPY EURJPY NZDJPY USDJPY GBPJPY AUDUSD EURUSD GBPUSD NZDUSD USDCAD USDCHF AUDCAD CADCHF EURCAD GBPCAD NZDCAD AUDCHF EURCHF GBPCHF NZDCHF EURAUD EURGBP EURNZD GBPNZD GBPAUD AUDNZD'''
#fx_pairs='EURUSD' #you can trade specific pairs if you desire
fx_pairs=fx_pairs.replace(' ','')
counter1=(len(fx_pairs)/6)

mt4_location="C:\\Users\\t\\AppData\\Roaming\\MetaQuotes\\Terminal\\61007F75C6EC7CED9A269B292061D7A1\\MQL4\\Files\\LastSignal.csv"
print(mt4_location)
while counter1>0:
    string=fx_pairs[-6:]
    fx_pairs=fx_pairs[0:-6]
    counter1=counter1-1
    df = pd.read_csv(path+'Pythonic Fx\\WinPython\\Forex OHLC\\'+string+'.csv')
    df=df.drop('Unnamed: 0', 1)
    df=df.drop('complete', 1)
    df=df.drop('time', 1)
    df=df.drop('volume', 1)
    #print(df.head)
    #print(df.tail)
    print('Obtained ', string,' data!')
    #####MATH#######
    MA_ARRAY_13=talib.EMA(np.array(df.close), timeperiod=13)
    RSI_ARRAY_13=talib.RSI(MA_ARRAY_13, timeperiod=13)
    MA_RSI_OMA_21=talib.EMA(RSI_ARRAY_13, timeperiod=21)
    MA_RSI_OMA_137=talib.EMA(RSI_ARRAY_13, timeperiod=137)
    print(RSI_ARRAY_13[-10:])
    print(MA_RSI_OMA_21[-10:])
    print(MA_RSI_OMA_137[-10:])
    #time.sleep(5)
    ##### Trade conditions###
    current_price=df.tail(1)
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
            if MA_RSI_OMA_21[-1] > RSI_ARRAY_13[-1] and MA_RSI_OMA_137[-1] > RSI_ARRAY_13[-1]:#LONG
                Pair=string
                signal='OP_BUY'
                SL=Long_SL
                TP=Long_TP
                place_order = pd.DataFrame({'': [Pair+','+signal+','+str(SL)+','+str(TP),',,,']})
                #automatically determines file locations string to match your own system
                place_order = place_order.to_csv(path+"Pythonic Fx\\MT4 Portable\\MQL4\\Files\\LastSignal.csv", header=None, index=None, mode='w', sep=' ',quoting=csv.QUOTE_NONE, quotechar="-",  escapechar="-")
                print(string+' pair has opened long')
                print('===============================')
                time.sleep(5)
				#insert optional oanda code here later for order tracking
                
        elif MA_RSI_OMA_21[-1] > 85:
            if MA_RSI_OMA_21[-1] < RSI_ARRAY_13[-1] and MA_RSI_OMA_137[-1] < RSI_ARRAY_13[-1]:#SHORT
                Pair=string
                signal='OP_SELL'
                SL=Short_SL
                TP=Short_TP
                place_order = pd.DataFrame({'': [Pair+','+signal+','+str(SL)+','+str(TP),',,,']})
                #automatically determines file locations string to match your own system
                place_order = place_order.to_csv(path+"Pythonic Fx\\MT4 Portable\\MQL4\\Files\\LastSignal.csv", header=None, index=None, mode='w', sep=' ',quoting=csv.QUOTE_NONE, quotechar="-",  escapechar="-")
                print(string+' pair has opened long')
                print('===============================')
                time.sleep(5)
				#insert optional oanda code here later for current order tracking
        else:
            print(string+' does not valid conditions to make trade')
            print('===============================')
            time.sleep(5)
            
    else:
        print('that particular pair is in trade')
        print('===============================')
        time.sleep(5)
#this is a trading bot i made for a friend as a demonstration, it is not profitable. 
#it is best to place orders on your mt4 broker and oanda api demo simultaneously; so you can use the oanda api to track open orders for your mt4 broker
#below is code that will place orders to oanda api 

#code that is used for shorting, insert in the shorting section of code
#for longing, modify the varibiles and insert to longing section of code                    ''
'''
api = oandapyV20.API(access_token='b1820d124857b58655e36eaa7f856b50-f9269344d4a6e789a9ce102df15af97d')#api key is expired

mktOrder = MarketOrderRequest(
    instrument=str(string[0:3]+'_'+string[3:6]),
    units=-10000, #longing is positive number
    takeProfitOnFill=TakeProfitDetails(price=Short_TP).data,
    stopLossOnFill=StopLossDetails(price=Short_SL).data)
r = orders.OrderCreate('101-002-10197028-005',data=mktOrder.data)
try:
    rv = api.request(r)
except oandapyV20.exceptions.V20Error as err:
    print(r.status_code, err)
else:
    print(json.dumps(rv, indent=2))
'''
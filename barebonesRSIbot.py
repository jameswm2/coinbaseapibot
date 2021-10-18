

import cbpro
import time
import pandas as pd
import pandas_ta as pta
import numpy as np

key= #PUBLIC KEY
b64secret= # PRIVATE KEY
passphrase= # PASSPHRASE (USED FOR SOME APPS)
auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)
accounts = auth_client.get_accounts()

sums = 0
for acc in accounts:
    sums += float(acc['balance']) # Check wallet USD balances
print(sums)
## this gives total USD value

ticker = auth_client.get_product_ticker(product_id='BTC-USD') ## public API pricing data
hist = pd.DataFrame()

def rma(x, n, y0):
    a = (n-1) / n
    ak = a**np.arange(len(x)-1, -1, -1)
    return np.r_[np.full(n, np.nan), y0, np.cumsum(ak * x) / ak / n + y0 * a**np.arange(1, len(x)+1)]

i=0
print("Starting USD: $100")
currentUSD = 100
currentBTC = 0
tradehist = pd.DataFrame()
tradedf = pd.DataFrame()

#BOT LOOP, YOU CAN REPLACE THIS WITH ACTUAL API CALLS FOR TRADES
while True:
    ticker = auth_client.get_product_ticker(product_id='BTC-USD')
    ticker['trade_id'] = [ticker['trade_id']]
    ticker['price'] = [float(ticker['price'])]
    ticker['size'] = [float(ticker['size'])]
    ticker['time'] = [ticker['time']]
    ticker['bid'] = [float(ticker['bid'])]
    ticker['ask'] = [float(ticker['ask'])]
    ticker['volume'] = [float(ticker['volume'])]
    ticker = pd.DataFrame.from_dict(ticker)
    hist = hist.append(ticker)
    


    n = 4 ## RSI period
    if i > n:
        hist['change'] = hist['price'].diff()
        hist['gain'] = hist.change.mask(hist.change < 0, 0.0)
        hist['loss'] = -hist.change.mask(hist.change > 0, -0.0)
        hist['avg_gain'] = rma(hist.gain[n+1:].to_numpy(), n, np.nansum(hist.gain.to_numpy()[:n+1])/n)
        hist['avg_loss'] = rma(hist.loss[n+1:].to_numpy(), n, np.nansum(hist.loss.to_numpy()[:n+1])/n)
        hist['rs'] = hist.avg_gain / hist.avg_loss
        hist['rsi_14'] = 100 - (100 / (1 + hist.rs))
        if hist['rsi_14'].iloc[-1] < 35:
            hist['buy'] = 1
            if currentUSD != 0:
                currentBTC = currentUSD/hist['price'].iloc[-1]
                currentUSD = 0
                tradedf["Type"] = "Buy"
                tradedf["BTC"] = currentBTC
                tradedf["USD"] = currentUSD
                tradedf["ind value"] = 6+i
                tradehist = tradehist.append(tradedf)
                print("Trade Made; ","USD: ",currentUSD,"BTC: ",currentBTC, "BTC Price: ", hist['price'].iloc[-1])

        else:
            hist['buy'] = 0
        if hist['rsi_14'].iloc[-1] > 70:
            hist['sell'] = 1
            if currentBTC != 0:
                currentUSD = currentBTC*hist['price'].iloc[-1]
                currentBTC = 0
                tradedf["Type"] = "Sell"
                tradedf["BTC"] = currentBTC
                tradedf["USD"] = currentUSD
                tradedf["ind value"] = 6+i
                tradehist = tradehist.append(tradedf)
                print("Trade Made; ","USD: ",currentUSD,"BTC: ",currentBTC, "BTC Price: ", hist['price'].iloc[-1])
        else:
            hist['sell'] = 0
        #print(hist[['price', 'rsi_14','buy','sell']].iloc[-1:].to_markdown(index=False),"USD:", currentUSD,"BTC: ", currentBTC)
    i+=1
    time.sleep(1) ## time between API calls, period of RSI interval

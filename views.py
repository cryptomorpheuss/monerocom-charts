from django.shortcuts import render
from .models import Transaction, Data, Coin
from datetime import date, timedelta
from django.http import HttpResponseRedirect
from django.urls import reverse
import locale
import datetime
import math
import requests
import json
import pandas as pd
from django.utils import timezone
import pygsheets
import tempfile
from django.contrib.auth.decorators import login_required

#########################################
######## Useful functions
#########################################

# Get price history for any coin and updtade the most recent missing prices
def get_prices(symbol):
    if symbol == 'btc':
        date_aux1 = '2011-05-30'
    if symbol == 'zec':
        date_aux1 = '2016-11-25'
    if symbol == 'grin':
        date_aux1 = '2019-07-03'
    if symbol == 'dash':
        date_aux1 = '2014-04-18'
    if symbol == 'xmr':
        date_aux1 = '2014-06-15'

    now = datetime.datetime.now()
    current_time = int(now.strftime("%H"))
    test = True
    updated = False

    coins = Coin.objects.filter(name=symbol).order_by('date')
    if not(coins):
        #print('here 1')
        start_time = '2011-01-01'
        end_time = date.today()
        end_time = datetime.datetime.strftime(end_time, '%Y-%m-%d')
    else:
        #print('here 2')
        for coin in coins:
            break

        date_aux1 = datetime.datetime.strptime(date_aux1, '%Y-%m-%d')
        date_aux2 = datetime.datetime.strftime(coin.date, '%Y-%m-%d')
        date_aux2 = datetime.datetime.strptime(date_aux2, '%Y-%m-%d')
        if date_aux2 > date_aux1:
            #print('here 3')
            start_time = '2008-01-01'
            end_time = coin.date - timedelta(1)
            end_time = datetime.datetime.strftime(end_time, '%Y-%m-%d')
        else:
            #print('here 4')
            for coin in coins:
                pass

            date_aux1 = date.today()-timedelta(2)
            #print('mais recente do banco de dados = ' + str(coin.date))
            #print('date_aux1 = ' + str(date_aux1))
            if (coin.date == date_aux1) and current_time >= 5 or (coin.date < date_aux1):
                #print('here 5')
                start_time = coin.date
                start_time = datetime.datetime.strftime(start_time, '%Y-%m-%d')
                end_time = date.today()-timedelta(1)
                end_time = datetime.datetime.strftime(end_time, '%Y-%m-%d')
            else:
                return updated

    request = ''
    while test: 
        response = requests.get(request)
        data = json.loads(response.text)
        if data['data']:
            data_aux = data['data']
        else:
            return False
        for item in data_aux:
            day, hour = str(item['time']).split('T')
            day = datetime.datetime.strptime(day, '%Y-%m-%d')
            day = datetime.datetime.strftime(day, '%Y-%m-%d')
            coins = Coin.objects.filter(name=symbol).filter(date=day)
            if coins:
                pass
            if item['SplyCur'] != None:
                if float(item['SplyCur']) >= 1:
                    try:
                        coin = Coin()
                        coin.name = symbol
                        coin.date = day
                        coin.supply = float(item['SplyCur'])
                        coin.priceusd = float(item['PriceUSD'])
                        coin.pricebtc = float(item['PriceBTC'])
                        coin.inflation = float(item['IssContPctAnn'])
                        coin.transactions = float(item['TxCnt'])

                        if symbol == 'xmr' or symbol == 'btc':
                            coin.stocktoflow = (100/coin.inflation)**1.65
                            coin.hashrate = float(item['HashRate'])
                            coin.fee = float(item['FeeTotNtv'])
                            coin.revenue = float(item['RevNtv'])
                        else:
                            coin.stocktoflow = 0
                            coin.hashrate = 0
                            coin.fee = 0
                            coin.revenue = 0
                        coin.save()
                        updated = True
                    except:
                        test = False
                else:
                    test = False
            else:
                test = False

            print(coin.name + ' - date = ' + str(coin.date) + ' - ' + str(test))
        try:
            request = data['next_page_url']
            #print(request)
        except:
            test = False

    return updated

@login_required
def generate_data(request=None):
    print('generating data for database...')
    data = Data.objects.all().delete()
    transaction = Transaction.objects.all().delete()
    print('data deleted')

    timevar = 1283
    symbol = 'xmr'
    v0 = 0.002
    delta = (0.015 - 0.002)/(6*365)
    count = 0
    supply = 0
    stock = 0.000001

    sf_aux = 0
    start_inflation = 0
    count2 = 0
    coins = Coin.objects.order_by('date').filter(name=symbol)
    print('generating data...')
    for coin in coins:
        data = Data()
        data.XMR_price_usd = coin.priceusd
        data.XMR_price_btc = coin.pricebtc
        data.date = coin.date
        date_aux1 = datetime.datetime.strptime('2017-12-29', '%Y-%m-%d')
        date_aux2 = datetime.datetime.strftime(coin.date, '%Y-%m-%d')
        date_aux2 = datetime.datetime.strptime(date_aux2, '%Y-%m-%d')
        if date_aux2 < date_aux1:
            lastprice = coin.priceusd
            start_inflation = coin.inflation
            current_inflation = start_inflation
            data.XMR_grey_line = 0
            count2 = 0
        else:
            day = date_aux2 - timedelta(timevar)
            try:
                coin_aux1 = Coin.objects.filter(name=symbol).get(date=day)
                day = date_aux2 - timedelta(timevar+1)
                coin_aux2 = Coin.objects.filter(name=symbol).get(date=day)
                date_aux3 = datetime.datetime.strptime('2017-12-29', '%Y-%m-%d')
            except:
                get_prices(symbol)
                return
            
            if date_aux3 + timedelta(int(count2*2)) < datetime.datetime.strptime('2021-07-03', '%Y-%m-%d'):
                day = date_aux3 + timedelta(int(count2*2))
                coin_aux3 = Coin.objects.filter(name=symbol).get(date=day)
                if coin_aux3:
                    if (coin_aux3.inflation/current_inflation) > 1.2 or (coin_aux3.inflation/current_inflation) < 0.8:
                        coin_aux3.inflation = current_inflation
                    else:
                        current_inflation = coin_aux3.inflation
                supply2 = supply
            else:
                reward2 = (2**64 -1 - supply2) >> 19
                if reward2 < 0.6*(10**12):
                    reward2 = 0.6*(10**12)
                supply2 += int(720*reward2)
                current_inflation = 100*reward2*720*365/supply2
                
            if coin_aux1 and coin_aux2:
                lastprice += (coin_aux1.priceusd/coin_aux2.priceusd-1)*lastprice
                actualprice = lastprice*(math.sqrt(start_inflation/current_inflation))
                data.XMR_grey_line = actualprice
            else:
                data.XMR_grey_line = 0

        if coin.priceusd < 0.01:
            coin.priceusd = 0.01

        if coin.inflation > 0:
            stock_to_flow = (100/coin.inflation)**1.65
        else:
            stock_to_flow = sf_aux
        if stock_to_flow < 0.2:
            stock_to_flow = 0
        if stock_to_flow > sf_aux*1.5+100:
            stock_to_flow = sf_aux
        sf_aux = stock_to_flow

        new_color = 31*coin.pricebtc/(count*delta + v0)-5.5
        data.XMR_color = new_color
        supply = int(coin.supply)*10**12
        data.XMR_stock_to_flow = stock_to_flow
        count += 1
        count2 += 1
        data.save()

    count = 0
    for count in range(650):
        data = Data()
        date_now = date.today() + timedelta(count)
        data.date = datetime.datetime.strftime(date_now, '%Y-%m-%d')
        reward = (2**64 -1 - supply) >> 19
        if reward < 0.6*(10**12):
            reward = 0.6*(10**12)
        supply += int(720*reward)
        inflation = 100*reward*720*365/supply
        stock = (100/(inflation))**1.65
        data.XMR_stock_to_flow = stock    
        data.XMR_color = 0
        data.XMR_price_usd = 0
        data.XMR_price_btc = 0
        data.XMR_grey_line = 0
        data.save()      

    print('generating transactions...')
    coins_btc = Coin.objects.order_by('date').filter(name='btc')
    for coin_btc in coins_btc:
        transaction = Transaction()
        transaction.date = coin_btc.date
        if coin_btc.transactions >= 1:
            transaction.btc = coin_btc.transactions
        else:
            transaction.btc = 0

        try:
            coin_dash = Coin.objects.filter(name='dash').get(date=coin_btc.date)
            transaction.dash = coin_dash.transactions
        except:
            transaction.dash = 0
        try:
            coin_xmr = Coin.objects.filter(name='xmr').get(date=coin_btc.date)
            transaction.xmr = coin_xmr.transactions
        except:
            transaction.xmr = 0
        try:
            coin_zcash = Coin.objects.filter(name='zec').get(date=coin_btc.date)
            transaction.zcash = coin_zcash.transactions
        except:
            transaction.zcash = 0
        try:
            coin_grin = Coin.objects.filter(name='grin').get(date=coin_btc.date)
            transaction.grin = coin_grin.transactions
        except:
            transaction.grin = 0
        transaction.save()
        
    return HttpResponseRedirect(reverse('index'))

def update_database():
    then = date.today() - timedelta(5)
    now = date.today() + timedelta(1)
    coins = Coin.objects.filter(name='xmr').filter(date__range=[then, now])
    print('updating database...')
    for coin in coins:
        try:
            data = Data.objects.get(date=coin.date)
        except:
            data = Data()
            data.XMR_price_usd = 0
            data.XMR_price_btc = 0
            data.XMR_stock_to_flow = 0
            data.XMR_grey_line = 0
            data.XMR_color = 0
            data.date = coin.date
            
        if data.XMR_price_btc == 0:
            data.XMR_price_btc = coin.pricebtc
        
        if data.XMR_price_usd == 0:
            data.XMR_price_usd = coin.priceusd

        if data.XMR_stock_to_flow == 0:
            supply = int(coin.supply)*10**12
            reward = (2**64 -1 - supply) >> 19
            if reward < 0.6*(10**12):
                reward = 0.6*(10**12)
            inflation = 100*reward*720*365/supply
            data.XMR_stock_to_flow = (100/(inflation))**1.65

        if data.XMR_color == 0:
            v0 = 0.002
            delta = (0.015 - 0.002)/(6*365)
            data.XMR_color = 30*coin.pricebtc/(int(coin.id)*delta + v0)

        data.save()
        print('salva 1')

    return

@login_required
def erase_database(request):
    data = Data.objects.all().delete()
    coins = Coin.objects.all().delete()
    print('database erased')
    context = {}
    return render(request, 'charts/erased.html', context)

@login_required
def erase_data(request):
    data = Data.objects.all().delete()
    print('data erased')
    context = {}
    return render(request, 'charts/erased.html', context)

@login_required
def erase_coins(request):
    coins = Coin.objects.all().delete()
    print('coins erased')
    context = {}
    return render(request, 'charts/erased.html', context)

def maintenance(request):
    context = {}
    return render(request, 'charts/maintenance.html', context)
    return

#########################################
######## Views functions for pages 
#########################################

# Create your views here.
def sf(request, scale):
    #erase_database()
    symbol = 'btc'
    get_prices(symbol)
    symbol = 'dash'
    get_prices(symbol)
    symbol = 'grin'
    get_prices(symbol)
    symbol = 'zec'
    get_prices(symbol)
    symbol = 'xmr'
    updated = get_prices(symbol)

    if updated:
        update_database()

    dates = []
    stock_to_flow = []
    projection = []
    color = []
    values = []
    now_price = 0
    now_sf = 0
    now_inflation = 0

    data = Data.objects.order_by('date')
    count_aux = 0
    for item in data:
        if item.XMR_color != 0:
            color.append(item.XMR_color)
        else:
            color.append('')

        if item.XMR_grey_line != 0:
            projection.append(item.XMR_grey_line)
            if count_aux > 25:
                count_aux = 0
            else:
                projection.append(item.XMR_grey_line)
        else:
            projection.append('')

        if item.XMR_stock_to_flow != 0:
            stock_to_flow.append(item.XMR_stock_to_flow)
        else:
            stock_to_flow.append('')

        if item.XMR_price_usd != 0:
            values.append(item.XMR_price_usd)
            now_price = item.XMR_price_usd
            now_sf = item.XMR_stock_to_flow
            if item.date > date.today() - timedelta(4):
                coins = Coin.objects.filter(name='xmr').filter(date=item.date)
                if coins:
                    for coin in coins:
                        now_inflation = coin.inflation
        else:
            values.append('')
        count_aux += 1
    
        dates.append(datetime.datetime.strftime(item.date, '%Y-%m-%d'))

    now_price = "$"+ locale.format('%.2f', now_price, grouping=True)
    now_sf = "$"+ locale.format('%.2f', now_sf, grouping=True)
    now_inflation = locale.format('%.2f', now_inflation, grouping=True)+'%'

    if scale == 'log':
        context = {'values': values, 'dates': dates, 'stock_to_flow': stock_to_flow, 'projection': projection,
        'now_price': now_price, 'now_inflation': now_inflation, 'now_sf': now_sf, 'color': color}
        return render(request, 'charts/sfmodel.html', context)
    else: 
        context = {'values': values, 'dates': dates, 'stock_to_flow': stock_to_flow,
        'now_price': now_price, 'now_inflation': now_inflation, 'now_sf': now_sf, 'color': color}
        return render(request, 'charts/sfmodellin.html', context)

def price(request, scale):
    dates = []
    color = []
    values = []
    maximum = 0

    data = Data.objects.order_by('date')
    for item in data:
        if item.XMR_color != 0:
            color.append(item.XMR_color)
        else:
            color.append('')

        if item.XMR_price_usd != 0:
            if item.XMR_price_usd > maximum:
                maximum = item.XMR_price_usd
            values.append(item.XMR_price_usd)
            now_price = item.XMR_price_usd
            now_sf = item.XMR_stock_to_flow
            if item.date > date.today() - timedelta(4):
                coins = Coin.objects.filter(name='xmr').filter(date=item.date)
                if coins:
                    for coin in coins:
                        now_inflation = coin.inflation
        else:
            values.append('')
    
        dates.append(datetime.datetime.strftime(item.date, '%Y-%m-%d'))

    now_price = "$"+ locale.format('%.2f', now_price, grouping=True)
    now_sf = "$"+ locale.format('%.2f', now_sf, grouping=True)
    maximum = "$"+ locale.format('%.2f', maximum, grouping=True)
    now_inflation = locale.format('%.2f', now_inflation, grouping=True)+'%'

    context = {'values': values, 'dates': dates, 'maximum': maximum, 'now_price': now_price, 'now_inflation': now_inflation, 'now_sf': now_sf, 'color': color}
    if scale == 'log':
        return render(request, 'charts/pricelog.html', context)
    else:
        return render(request, 'charts/pricelin.html', context)

def price_btc(request, scale):
    bottom = 1
    dates = []
    color = []
    values = []
    maximum = 0

    data = Data.objects.order_by('date')
    for item in data:
        if item.XMR_color != 0:
            color.append(item.XMR_color)
        else:
            color.append('')

        if item.XMR_price_btc != 0:
            if item.XMR_price_btc > 0.0000001 and item.XMR_price_btc < bottom:
                bottom = item.XMR_price_btc
            if item.XMR_price_btc > maximum:
                maximum = item.XMR_price_btc
            values.append(item.XMR_price_btc)
            now_price = item.XMR_price_btc
        else:
            values.append('')
    
        dates.append(datetime.datetime.strftime(item.date, '%Y-%m-%d'))
    
    now_price = locale.format('%.4f', now_price, grouping=True) + ' BTC'
    maximum = locale.format('%.4f', maximum, grouping=True) + ' BTC'
    bottom = locale.format('%.4f', bottom, grouping=True) + ' BTC'

    context = {'values': values, 'dates': dates, 'maximum': maximum, 'now_price': now_price, 'color': color, 'bottom': bottom}
    if scale == 'log':
        return render(request, 'charts/pricesatslog.html', context)
    else:
        return render(request, 'charts/pricesats.html', context)

def pricesatslog(request):
    bottom = 1
    dates = []
    color = []
    values = []
    maximum = 0

    data = Data.objects.order_by('date')
    for item in data:
        if item.XMR_color != 0:
            color.append(item.XMR_color)
        else:
            color.append('')

        if item.XMR_price_btc != 0:
            if item.XMR_price_btc > 0.0000001 and item.XMR_price_btc < bottom:
                bottom = item.XMR_price_btc
            if item.XMR_price_btc > maximum:
                maximum = item.XMR_price_btc
            values.append(item.XMR_price_btc)
            now_price = item.XMR_price_btc
        else:
            values.append('')
    
        dates.append(datetime.datetime.strftime(item.date, '%Y-%m-%d'))
    
    now_price = locale.format('%.4f', now_price, grouping=True) + ' BTC'
    maximum = locale.format('%.4f', maximum, grouping=True) + ' BTC'
    bottom = locale.format('%.4f', bottom, grouping=True) + ' BTC'

    context = {'values': values, 'dates': dates, 'maximum': maximum, 'now_price': now_price, 'color': color, 'bottom': bottom}
    return render(request, 'charts/pricesatslog.html', context)

def cycle(request):
    dates = []
    color = []
    sell = []
    buy = []

    data = Data.objects.order_by('date')
    for item in data:
        if item.XMR_color > 0:
            color.append(item.XMR_color)
        else:
            color.append('')

        sell.append(100)
        buy.append(0)
        dates.append(datetime.datetime.strftime(item.date, '%Y-%m-%d'))

    context = {'dates': dates, 'color': color, 'sell': sell, 'buy': buy}
    return render(request, 'charts/cycle.html', context)

def sfmultiple(request):
    symbol = 'xmr'
    now_sf = 0
    dates = []
    stock_to_flow = []
    buy = []
    sell = []
    color = []
    v0 = 0.002
    delta = (0.015 - 0.002)/(6*365)
    count = 0

    sf_aux = 0 
    coins = Coin.objects.order_by('date').filter(name=symbol)
    for coin in coins:
        dates.append(datetime.datetime.strftime(coin.date, '%Y-%m-%d'))
        buy.append(1)
        sell.append(100)
        if coin.stocktoflow > sf_aux*2+250:
            coin.stocktoflow = sf_aux
        sf_aux = coin.stocktoflow
        if coin.priceusd < 1:
            coin.priceusd = 1
        if coin.stocktoflow != 0:
            now_sf = coin.supply*coin.priceusd/(coin.stocktoflow*1500000)
        stock_to_flow.append(now_sf)
        new_color = 30*coin.pricebtc/(count*delta + v0)
        color.append(new_color)
        count += 1  

    context = {'dates': dates, 'stock_to_flow': stock_to_flow, 'buy': buy, 'sell': sell, 'color': color}
    return render(request, 'charts/sfmultiple.html', context)

def inflationfractal(request):
    symbol = 'xmr'
    dates1 = []
    dates2 = []
    cycle1 = []
    cycle2 = []
    now_multiple = 0
    maximum = 0

    current_inflation = 0
    start_inflation = 0
    count1 = 1
    count2 = 1
    date1_aux = datetime.datetime(2017, 12, 29) 
    date2_aux = datetime.datetime(2014, 6, 21)
    coins = Coin.objects.order_by('date').filter(name=symbol)
    for coin in coins:
        date3_aux = datetime.datetime.combine(coin.date, datetime.time(0, 0))
        if date3_aux < date1_aux and date3_aux > date2_aux:
            start_inflation = coin.inflation
            current_inflation = start_inflation
            cycle1.append(coin.priceusd/5)
            dates1.append(count1/12.7)
            if (coin.priceusd/5) > maximum:
                maximum = coin.priceusd/5
            count1 += 1
        elif date3_aux > date1_aux:
            if (coin.inflation/current_inflation) > 1.15 or (coin.inflation/current_inflation) < 0.85:
                coin.inflation = current_inflation
            else:
                current_inflation = coin.inflation
            delta = math.sqrt(coin.inflation/start_inflation)
            cycle2.append(delta*coin.priceusd/477.12)
            dates2.append(count2/20.55) #24
            now_multiple = delta*coin.priceusd/477.12
            count2 += 0.86

    now_multiple = locale.format('%.2f', now_multiple, grouping=True) + 'x'
    maximum = locale.format('%.2f', maximum, grouping=True) + 'x'

    context = {'cycle1': cycle1, 'cycle2': cycle2, 'dates1': dates1, 'dates2': dates2, 'now_multiple': now_multiple, 'maximum': maximum}
    return render(request, 'charts/inflationfractal.html', context)

def golden(request):
    symbol = 'xmr'
    dates = []
    prices = []

    coins = Coin.objects.order_by('date').filter(name=symbol)
    for coin in coins:
        firstdate = coin.date
        break     

    day = firstdate - timedelta(350)
    for i in range(350):
        dates.append(datetime.datetime.strftime(day, '%Y-%m-%d'))
        prices.append(0.2)

    for coin in coins:
        dates.append(datetime.datetime.strftime(coin.date, '%Y-%m-%d'))
        if coin.priceusd > 0.2:
            prices.append(coin.priceusd)
        else:
            prices.append(0.2)
    
    n = 350
    median = pd.Series(prices).rolling(window=n).mean().iloc[n-1:].values
    m_350 = []
    m_350_0042 = []
    m_350_0060 = []
    m_350_0200 = []
    m_350_0300 = []
    m_350_0500 = []
    m_350_0800 = []
    m_350_1300 = []
    for i in range(350):
        m_350.append('')
        m_350_0042.append('')
        m_350_0060.append('')
        m_350_0200.append('')
        m_350_0300.append('')
        m_350_0500.append('')
        m_350_0800.append('')
        m_350_1300.append('')
    for item in median:
        m_350.append(float(item))
        m_350_0042.append(float(item)*0.42)
        m_350_0060.append(float(item)*0.60)
        m_350_0200.append(float(item)*2.00)
        m_350_0300.append(float(item)*3.00)
        m_350_0500.append(float(item)*5.00)
        m_350_0800.append(float(item)*8.00)
        m_350_1300.append(float(item)*13.00)

    n = 120
    median = pd.Series(prices).rolling(window=n).mean().iloc[n-1:].values
    m_111 = []
    for i in range(120):
        m_111.append('')
    for item in median:
        m_111.append(float(item))

    i = 0
    down = True
    price_cross = []
    for price in prices:
        if m_111[i] != '' and m_350_0200[i] != '':
            if down == True and m_111[i] > m_350_0200[i]:
                down = False
                price_cross.append(price)
            elif price > m_350_0500[i]:
                price_cross.append(price)
            elif down == False and m_111[i] < m_350_0200[i]:
                down = True
            else:
                price_cross.append('')
        else:
            price_cross.append('')
        i += 1

    context = {'dates': dates, 'prices': prices, 'm_350': m_350, 'm_350_0042': m_350_0042, 'm_350_0060': m_350_0060, 'm_350_0200': m_350_0200, 'm_350_0300': m_350_0300, 
    'm_350_0500': m_350_0500, 'm_350_0800': m_350_0800, 'm_350_1300': m_350_1300, 'median': median, 'm_111': m_111, 'price_cross': price_cross}
    return render(request, 'charts/golden.html', context)

def competitors(request):
    dates = []
    xmr = []
    dash = []
    grin = []
    zcash = []
    count = 0
    now_xmr = 0
    now_dash = 0
    now_grin = 0
    now_zcash = 0

    count = 0
    coins_xmr = Coin.objects.order_by('date').filter(name='xmr')
    for coin_xmr in coins_xmr:
        if coin_xmr.priceusd:
            if count > 30:
                xmr.append(coin_xmr.priceusd/5.01)
                now_xmr = coin_xmr.priceusd/5.01
            dates.append(count)
            count += 1
        elif count <= 63:
            continue
        else:
            xmr.append('')

    count = 0
    coins_dash = Coin.objects.order_by('date').filter(name='dash')
    for coin_dash in coins_dash:
        count += 1
        if coin_dash.priceusd and count > 130:
            dash.append(coin_dash.priceusd/14.7)
            now_dash = coin_dash.priceusd/14.7
        elif count <= 130:
            continue
        else:
            dash.append('')
        dates.append(count)

    count = 0
    coins_grin = Coin.objects.order_by('date').filter(name='grin')
    for coin_grin in coins_grin:
        count += 1
        if coin_grin.priceusd and count > 155:
            grin.append(coin_grin.priceusd/6.37)
            now_grin = coin_grin.priceusd/6.37
        elif count <= 155:
            continue
        else:
            grin.append('')
        dates.append(count)

    count = 0
    coins_zcash = Coin.objects.order_by('date').filter(name='zec')
    for coin_zcash in coins_zcash:
        count += 1
        if coin_zcash.priceusd and count > 434:
            zcash.append(coin_zcash.priceusd/750)
            now_zcash = coin_zcash.priceusd/750
        elif count <= 434:
            continue
        else:
            zcash.append('')
        dates.append(count)

    now_dash = locale.format('%.2f', now_dash, grouping=True) 
    now_grin = locale.format('%.2f', now_grin, grouping=True)
    now_zcash = locale.format('%.2f', now_zcash, grouping=True)
    now_xmr = locale.format('%.2f', now_xmr, grouping=True)

    context = {'xmr': xmr, 'dash': dash, 'grin': grin, 'zcash': zcash, 'now_xmr': now_xmr, 'now_dash': now_dash, 'now_grin': now_grin, 'now_zcash': now_zcash, 'dates': dates}
    return render(request, 'charts/competitors.html', context)

def inflationreturn(request):
    count = 0
    xmr = []
    dash = []
    grin = []
    zcash = []
    btc = []
    now_xmr = 0
    now_dash = 0
    now_grin = 0
    now_zcash = 0
    inflation_xmr = []
    inflation_dash = []
    inflation_grin = []
    inflation_zcash = []

    lastxmrA = 0
    lastxmrB = 0

    count = 0
    coins = Coin.objects.order_by('date').filter(name='xmr')
    for coin in coins:
        count += 1
        if coin.priceusd and count > 30:
            now_xmr = coin.priceusd/5.01
            #correcao de um erro nos dados
            if 100/coin.inflation > 110 and now_xmr < 10:
                xmr.append(lastxmrA)
                inflation_xmr.append(lastxmrB)
            else:
                xmr.append(now_xmr)
                inflation_xmr.append(100/coin.inflation)
                lastxmrA = now_xmr
                lastxmrB = 100/coin.inflation

    count = 0
    coins = Coin.objects.order_by('date').filter(name='dash')
    for coin in coins:
        count += 1
        if coin.priceusd and count > 130:
            now_dash = coin.priceusd/14.7
            dash.append(now_dash)
            inflation_dash.append(100/coin.inflation)

    count = 0
    coins = Coin.objects.order_by('date').filter(name='grin')
    for coin in coins:
        count += 1
        if coin.priceusd and count > 155:
            now_grin = coin.priceusd/6.37
            grin.append(now_grin)
            inflation_grin.append(100/coin.inflation)

    count = 0
    coins = Coin.objects.order_by('date').filter(name='zec')
    for coin in coins:
        count += 1
        if coin.priceusd and count > 434:
            now_zcash = coin.priceusd/750
            zcash.append(now_zcash)
            inflation_zcash.append(100/coin.inflation)

    now_dash = locale.format('%.2f', now_dash, grouping=True) 
    now_grin = locale.format('%.2f', now_grin, grouping=True)
    now_zcash = locale.format('%.2f', now_zcash, grouping=True)
    now_xmr = locale.format('%.2f', now_xmr, grouping=True)

    context = {'inflation_xmr': inflation_xmr, 'inflation_dash': inflation_dash, 'inflation_grin': inflation_grin, 'inflation_zcash': inflation_zcash, 'now_xmr': now_xmr, 
    'now_dash': now_dash, 'now_grin': now_grin, 'now_zcash': now_zcash, 'btc': btc, 'xmr': xmr, 'dash': dash, 'zcash': zcash, 'grin': grin}
    return render(request, 'charts/inflationreturn.html', context)

def shielded(request):
    dates = []
    values = []
    values2 = []
    values3 = []

    temp = tempfile.NamedTemporaryFile()
    temp.write(json.dumps({
        "type": "service_account",
        "project_id": "",
        "private_key_id": "",
        "private_key": "",
        "client_email": "",
        "client_id": "",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": ""
    }).encode('utf-8'))

    temp.flush()
    service_file = temp
    
    gc = pygsheets.authorize(service_file=service_file.name)
    sh = gc.open('zcash_bitcoin')
    wks = sh.worksheet_by_title('Sheet1')
    dominance = 0
    monthly = 0 
    
    values_mat = wks.get_values(start=(3,1), end=(999,5), returnas='matrix')

    for k in range(0,len(values_mat)):
        if values_mat[k][0] and values_mat[k][3]:
            date = values_mat[k][0]
            value = values_mat[k][3]
            value3 = values_mat[k][4]
            if not(value) or not(value):
                break
            else:
                dates.append(date)
                values.append(int(value))
                values3.append(int(value3))
        else:
            break
    
    previous_date = 0
    coins = Coin.objects.order_by('date').filter(name='xmr')
    for date in dates:
        value2 = 0
        for coin in coins:
            aux = str(coin.date)
            month = aux.split("-")[0] + '-' + aux.split("-")[1]
            if month == date:
                if previous_date != coin.date:
                    value2 += coin.transactions
                    previous_date = coin.date
        
        values2.append(int(value2))
    
    dominance = 100*int(value2)/(int(value2)+int(value)+int(value3))
    monthly = int(value2)

    context = {'dates': dates, 'values': values, 'values2': values2, 'values3': values3, "monthly": monthly, "dominance": dominance}
    return render(request, 'charts/shielded.html', context)

def total_transactions(request):
    transactions = Transaction.objects.order_by('date')

    dates = []
    txxmr = []
    txdash = []
    txgrin = []
    txzcash = []
    txbtc = []
    
    for transaction in transactions:
        dates.append(datetime.datetime.strftime(transaction.date, '%Y-%m-%d'))
        if transaction.btc > 0:
            txbtc.append(transaction.btc)
        else:
            txbtc.append('')
        if transaction.xmr > 0:
            txxmr.append(transaction.xmr)
        else: 
            txxmr.append('')
        if transaction.zcash > 0:
            txzcash.append(transaction.zcash)
        else:
            txzcash.append('')
        if transaction.dash > 0:
            txdash.append(transaction.dash)
        else:
            txdash.append('')
        if transaction.grin > 0:
            txgrin.append(transaction.grin)
        else:
            txgrin.append('')

    context = {'txxmr': txxmr, 'txdash': txdash, 'txgrin': txgrin, 'txzcash': txzcash, 'txbtc': txbtc, 'dates': dates}
    return render(request, 'charts/total_transactions.html', context)

#########################################
######## Old functions 
#########################################

# These might be needed in case we run into some king of error inside the database
# These don't use the database arguments, instead it calculate all lines using basic price metrics

def sf_old(request, scale):
    symbol = 'btc'
    get_prices(symbol)
    symbol = 'dash'
    get_prices(symbol)
    symbol = 'grin'
    get_prices(symbol)
    symbol = 'zec'
    get_prices(symbol)
    symbol = 'xmr'
    get_prices(symbol)

    timevar = 1283
    symbol = 'xmr'
    now_price = 0
    now_sf = 0
    now_inflation = 0.001
    v0 = 0.002
    delta = (0.015 - 0.002)/(6*365)
    count = 0
    maximum = 0
    supply = 0
    stock = 0.000001
    dates = []
    stock_to_flow = []
    projection = []
    color = []
    values = []

    sf_aux = 0
    skipped = 0
    start_inflation = 0
    count2 = 0
    coins = Coin.objects.order_by('date').filter(name=symbol)
    for coin in coins:
        dates.append(datetime.datetime.strftime(coin.date, '%Y-%m-%d'))
        values.append(coin.priceusd)
        date_aux1 = datetime.datetime.strptime('2017-12-29', '%Y-%m-%d')
        date_aux2 = datetime.datetime.strftime(coin.date, '%Y-%m-%d')
        date_aux2 = datetime.datetime.strptime(date_aux2, '%Y-%m-%d')
        if date_aux2 < date_aux1:
            lastprice = coin.priceusd
            start_inflation = coin.inflation
            current_inflation = start_inflation
            projection.append('')
            count2 = 0
        else:
            day = date_aux2 - timedelta(timevar)
            coin_aux1 = Coin.objects.filter(name=symbol).get(date=day)
            day = date_aux2 - timedelta(timevar+1)
            coin_aux2 = Coin.objects.filter(name=symbol).get(date=day)
            date_aux3 = datetime.datetime.strptime('2017-12-29', '%Y-%m-%d')
            
            if date_aux3 + timedelta(int(count2*2)) < datetime.datetime.strptime('2021-07-03', '%Y-%m-%d'):
                day = date_aux3 + timedelta(int(count2*2))
                coin_aux3 = Coin.objects.filter(name=symbol).get(date=day)
                if coin_aux3:
                    if (coin_aux3.inflation/current_inflation) > 1.2 or (coin_aux3.inflation/current_inflation) < 0.8:
                        coin_aux3.inflation = current_inflation
                    else:
                        current_inflation = coin_aux3.inflation
                supply2 = supply
            else:
                reward2 = (2**64 -1 - supply2) >> 19
                if reward2 < 0.6*(10**12):
                    reward2 = 0.6*(10**12)
                supply2 += int(720*reward2)
                current_inflation = 100*reward2*720*365/supply2
                
            if coin_aux1 and coin_aux2:
                lastprice += (coin_aux1.priceusd/coin_aux2.priceusd-1)*lastprice
                actualprice = lastprice*(math.sqrt(start_inflation/current_inflation))
                projection.append(actualprice)
                if skipped < 12:
                    projection.append(actualprice)
                else:
                    skipped = 0
            else:
                projection.append('')
            skipped += 1

        if coin.priceusd < 0.01:
            coin.priceusd = 0.01
        if coin.stocktoflow > sf_aux*2+250:
            coin.stocktoflow = sf_aux
        sf_aux = coin.stocktoflow
        if coin.stocktoflow < 0.1:
            coin.stocktoflow = 0.1
        now_inflation = coin.inflation
        now_price = coin.priceusd
        now_sf = coin.stocktoflow
        new_color = 31*coin.pricebtc/(count*delta + v0)-5.5
        color.append(new_color)
        supply = int(coin.supply)*10**12
        stock_to_flow.append(coin.stocktoflow)
        count += 1
        count2 += 1

    count = 0
    for count in range(650):
        date_now = date.today() + timedelta(count)
        dates.append(datetime.datetime.strftime(date_now, '%Y-%m-%d'))
        reward = (2**64 -1 - supply) >> 19
        if reward < 0.6*(10**12):
            reward = 0.6*(10**12)
        supply += int(720*reward)
        inflation = 100*reward*720*365/supply
        stock = (100/(inflation))**1.65
        stock_to_flow.append(stock)            

    now_price = "$"+ locale.format('%.2f', now_price, grouping=True)
    now_sf = "$"+ locale.format('%.2f', now_sf, grouping=True)
    maximum = "$"+ locale.format('%.2f', maximum, grouping=True)
    now_inflation = locale.format('%.2f', now_inflation, grouping=True)+'%'

    context = {'values': values, 'dates': dates, 'maximum': maximum, 'stock_to_flow': stock_to_flow, 'projection': projection, 'now_price': now_price, 'now_inflation': now_inflation, 'now_sf': now_sf, 'color': color}
    if scale == 'log':
        return render(request, 'charts/sfmodel.html', context)
    else: 
        return render(request, 'charts/sfmodellin.html', context)

def price_old(request, scale):
    symbol = 'xmr'
    now_price = 0
    now_sf = 0
    now_inflation = 0
    v0 = 0.002
    delta = (0.015 - 0.002)/(6*365)
    count = 0
    maximum = 0
    supply = 0
    dates = []
    color = []
    values = []

    coins = Coin.objects.order_by('date').filter(name=symbol)
    for coin in coins:
        dates.append(datetime.datetime.strftime(coin.date, '%Y-%m-%d'))
        values.append(coin.priceusd)
        if coin.priceusd < 0.01:
            coin.priceusd = 0.01
        if coin.stocktoflow < 0.1:
            coin.stocktoflow = 0.1
        now_inflation = coin.inflation
        now_price = coin.priceusd
        now_sf = coin.stocktoflow
        if now_price > maximum:
            maximum = now_price
        new_color = 31*coin.pricebtc/(count*delta + v0)-5.5
        color.append(new_color)
        supply = int(coin.supply)*10**12
        count += 1

    count = 0
    for count in range(650):
        date_now = date.today() + timedelta(count)
        dates.append(datetime.datetime.strftime(date_now, '%Y-%m-%d'))
        reward = (2**64 -1 - supply) >> 19
        if reward < 0.6*(10**12):
            reward = 0.6*(  10**12)
        supply += int(720*reward)

    now_price = "$"+ locale.format('%.2f', now_price, grouping=True)
    now_sf = "$"+ locale.format('%.2f', now_sf, grouping=True)
    maximum = "$"+ locale.format('%.2f', maximum, grouping=True)
    now_inflation = locale.format('%.2f', now_inflation, grouping=True)+'%'

    context = {'values': values, 'dates': dates, 'maximum': maximum, 'now_price': now_price, 'now_inflation': now_inflation, 'now_sf': now_sf, 'color': color}
    if scale == 'log':
        return render(request, 'charts/pricelog.html', context)
    else:
        return render(request, 'charts/pricelin.html', context)

def price_btc_old(request, scale):
    symbol = 'xmr'
    color = []
    values = []
    dates = []
    now_price = 0
    maximum = 0
    bottom = 1
    v0 = 0.002
    delta = (0.015 - 0.002)/(6*365)
    count = 0

    coins = Coin.objects.order_by('date').filter(name=symbol)
    for coin in coins:
        dates.append(datetime.datetime.strftime(coin.date, '%Y-%m-%d'))
        if coin.pricebtc > 0.001:
            values.append(coin.pricebtc)
        else:
            values.append('')
        date_aux1 = datetime.datetime.strptime('2021-03-15', '%Y-%m-%d')
        date_aux2 = datetime.datetime.strftime(coin.date, '%Y-%m-%d')
        date_aux2 = datetime.datetime.strptime(date_aux2, '%Y-%m-%d')
        if date_aux2 < date_aux1:
            lastprice = coin.pricebtc
        else:
            day = date_aux2 - timedelta(1700)
            coin_aux1 = Coin.objects.filter(name=symbol).get(date=day)
            day = date_aux2 - timedelta(1701)
            coin_aux2 = Coin.objects.filter(name=symbol).get(date=day)
            if coin_aux1 and coin_aux2:
                lastprice += (coin_aux1.pricebtc/coin_aux2.pricebtc-1)*lastprice*0.75
        if coin.pricebtc > 0:
            now_price = coin.pricebtc
        if now_price > maximum:
            maximum = now_price
        if now_price > 0:
            if now_price < bottom:
                bottom = now_price
        new_color = 31*coin.pricebtc/(count*delta + v0)-5.5
        color.append(new_color)
        count += 1

    count = 0
    for count in range(300):
        date_now = date.today() + timedelta(count)
        dates.append(datetime.datetime.strftime(date_now, '%Y-%m-%d'))
        day = date_now - timedelta(1900)
        coin_aux1 = Coin.objects.filter(name=symbol).get(date=day)
        day = date_now - timedelta(1901)
        coin_aux2 = Coin.objects.filter(name=symbol).get(date=day)
        if coin_aux1 and coin_aux2:
            lastprice += (coin_aux1.pricebtc/coin_aux2.pricebtc-1)*lastprice*0.75
    
    now_price = locale.format('%.4f', now_price, grouping=True) + ' BTC'
    maximum = locale.format('%.4f', maximum, grouping=True) + ' BTC'
    bottom = locale.format('%.4f', bottom, grouping=True) + ' BTC'

    context = {'values': values, 'dates': dates, 'maximum': maximum, 'now_price': now_price, 'color': color, 'bottom': bottom}
    if scale == 'log':
        return render(request, 'charts/pricesatslog.html', context)
    else:
        return render(request, 'charts/pricesats.html', context)

def cycle_old(request):
    dates = []
    color = []
    sell = []
    buy = []

    symbol = 'xmr'
    v0 = 0.002
    delta = (0.015 - 0.002)/(6*365)
    count = 0

    coins = Coin.objects.order_by('date').filter(name=symbol)
    for coin in coins:
        if coin.pricebtc > 0:
            color.append(31*coin.pricebtc/(count*delta + v0)-5.5)
            sell.append(100)
            buy.append(0)
            dates.append(datetime.datetime.strftime(coin.date, '%Y-%m-%d'))

    context = {'dates': dates, 'color': color, 'sell': sell, 'buy': buy}
    return render(request, 'charts/cycle.html', context)

def total_transactions_old(request):
    coins_btc = Coin.objects.order_by('date').filter(name='btc')

    dates = []
    txxmr = []
    txdash = []
    txgrin = []
    txzcash = []
    txbtc = []
    count = 0
    
    for coin_btc in coins_btc:
        count += 1
        if coin_btc.transactions > 0.1:
            txbtc.append(coin_btc.transactions)
        else:
            txbtc.append('')
        dates.append(datetime.datetime.strftime(coin_btc.date, '%Y-%m-%d'))
        if count < 500:
            txdash.append('')
            txxmr.append('')
        else:
            coins_dash = Coin.objects.filter(name='dash').filter(date=coin_btc.date)
            if coins_dash:
                for coin_dash in coins_dash:
                    if coin_dash.transactions > 0.1:
                        txdash.append(coin_dash.transactions)
                    else:
                        txdash.append('')
            else:
                txdash.append('')
            coins_xmr = Coin.objects.filter(name='xmr').filter(date=coin_btc.date)
            if coins_xmr:
                for coin_xmr in coins_xmr:
                    if coin_xmr.transactions > 0.1:
                        txxmr.append(coin_xmr.transactions)
                    else:
                        txxmr.append('')
            else:
                txxmr.append('')

        if count < 1400:
            txzcash.append('')
        else:
            coins_zcash = Coin.objects.filter(name='zec').filter(date=coin_btc.date)
            if coins_zcash:
                for coin_zcash in coins_zcash:
                    if coin_zcash.transactions > 0.1:
                        txzcash.append(coin_zcash.transactions)
                    else:
                        txzcash.append('')
            else:
                txzcash.append('')

        if count < 1800:
            txgrin.append('')
        else:
            coins_grin = Coin.objects.filter(name='grin').filter(date=coin_btc.date)
            if coins_grin:
                for coin_grin in coins_grin:
                    if coin_grin.transactions > 0.1:
                        txgrin.append(coin_grin.transactions)
                    else:
                        txgrin.append('')
            else:
                txgrin.append('')

    context = {'txxmr': txxmr, 'txdash': txdash, 'txgrin': txgrin, 'txzcash': txzcash, 'txbtc': txbtc, 'dates': dates}
    return render(request, 'charts/total_transactions.html', context)

















import logging

import cbpro
from vardata import numberMaxCryptosToInvest, lessHight, profit, fees, defaultPortofolio
import cryptoCalculations
import requests
from requests.auth import AuthBase
import time
import base64, hashlib, hmac
import numpy
from _decimal import Decimal
import math
from datetime import datetime


def buyAndSellCoinbase(dictionaryCryptos, priorityCoinsList, auth_client, MongoClient):
    if len(dictionaryCryptos) == 0:
        return None;

    print("*********************************************************************************************************")
    print("*                                                                                                       *")
    print("*                                                                                                       *")
    print("*                                                                                                       *")
    print("*                                             Começo da compra                                                      *")
    print("*                                                                                                       *")
    print("*                                                                                                       *")
    print("*                                                                                                       *")
    print("*********************************************************************************************************")

    db = MongoClient.cryptoHistoric

    profileEUR = auth_client.get_account(getattr(dictionaryCryptos["Euro"], "profileCoinbaseID"))

    print(profileEUR["available"])
    moneyEUR = profileEUR["available"]

    if float(moneyEUR) == 0:
        return None

    orders = auth_client.get_orders()

    print(orders)

    quantityCryprosInvested = 0 #Actual cryptos quantity already invested
    for item in orders:
        print(item)
        if item["side"] == 'sell' and item["type"] == 'limit':
            quantityCryprosInvested += 1

    print("quantidade order:",quantityCryprosInvested)



    quantityToInvest = 0 #Quantity to Invest

    if quantityCryprosInvested >= numberMaxCryptosToInvest:
        return None;

    #for i in range(quantityCryprosInvested + 1):
        #print("iteração")
        #if quantityCryprosInvested == i:
            #print("entrou dentro do if")
            #d = quantityCryprosInvested - i
            #print("O d:",d)
            #if d == 0:
                #"d é igual a 0"
                #d = 1
            #quantityToInvest = float(moneyEUR) / d
            #print("quantidade para investir:",quantityToInvest)
            #break


    #Know if the coin is already buyed

    # vai ver no array o que compensa mais
    priorityCoinsList.sort(reverse=True)
    print(priorityCoinsList)
    priorityCoinsList = numpy.array(priorityCoinsList)
    isCoinFinded = False
    CoinFinded = None
    isStillWorthIt = False
    percentageBelow = 0


    for item in priorityCoinsList:
        print(item)

        for d in dictionaryCryptos:
            print(item," é o do array e ",d,"é do dcioario")
            if item[1] == getattr(dictionaryCryptos[d],"name"):
                cryptoAccount = auth_client.get_account(getattr(dictionaryCryptos[d], "profileCoinbaseID"))
                print("conta: ",cryptoAccount)
                if float(cryptoAccount['hold']) != 0:
                    isCoinFinded = False
                else:
                    print("é trueeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
                    isCoinFinded = True
                    CoinFinded = d
                    percentageBelow = float(item[0])


                    print("moeda encontrada ", CoinFinded)
                    # Verify if the coin is still worth it
                    lastValue = cryptoCalculations.knowLastValue(
                        getattr(dictionaryCryptos[CoinFinded], "codeCoinbase") + "-EUR")
                    print(lastValue)

                    if lastValue['type'] == 'ticker':
                        collection = db[getattr(dictionaryCryptos[CoinFinded], "name")]
                        historic = collection.find()

                        for his in historic:
                            highter = max(his["WeekOne"][1], his["WeekTwo"][1], his["WeekThree"][1], his["WeekFour"][1])
                            minimum = min(his["WeekOne"][0], his["WeekTwo"][0], his["WeekThree"][0],his["WeekFour"][0])

                            print(highter)
                            atualPrice = float(lastValue["price"])
                            #x = (highter - atualPrice) / highter
                            #print(x)
                            #percentage = x * 100

                            range = highter - minimum
                            correctedStartValue = atualPrice - minimum
                            percentage = (correctedStartValue * 100) / range

                            percentage = 100 - percentage

                            print("Is Less : ", percentage, "%")

                            print(lessHight)

                            if lessHight <= percentage and (percentage - 3) <= percentageBelow:
                                isStillWorthIt = True
                            else:
                                continue
            if isStillWorthIt == True:
                quantityToInvest = float(moneyEUR) / (numberMaxCryptosToInvest - quantityCryprosInvested)

                print("Quantidade decidida:", quantityToInvest)

                if float(getattr(dictionaryCryptos[CoinFinded], "min")) > quantityToInvest or float(getattr(dictionaryCryptos[CoinFinded], "minCryptoSell")) > (quantityToInvest / float(lastValue["price"])):
                    if float(getattr(dictionaryCryptos[CoinFinded], "min")) <= float(moneyEUR):
                        quantityToInvest = float(getattr(dictionaryCryptos[CoinFinded], "min"))
                        print("Minimo agora: ",float(getattr(dictionaryCryptos[CoinFinded], "minCryptoSell")))
                        if float(getattr(dictionaryCryptos[CoinFinded], "minCryptoSell")) > (quantityToInvest / float(lastValue["price"])):
                            if (float(getattr(dictionaryCryptos[CoinFinded], "minCryptoSell")) * float(lastValue["price"]) * 1.10) < float(moneyEUR):
                                quantityToInvest = float(getattr(dictionaryCryptos[CoinFinded], "minCryptoSell")) * float(lastValue["price"])
                                quantityToInvest = quantityToInvest * 1.10
                            else:
                                print("Dont have minimum to sell")
                                isStillWorthIt = False
                    else:
                        print("Dont have minimum to buy")
                        isStillWorthIt = False

            if isStillWorthIt == True:
                print('Moeda e: ' + getattr(dictionaryCryptos[CoinFinded], "codeCoinbase") + '-EUR')
                print("quantidade para investir: ", quantityToInvest)

                maxPrecision = getattr(dictionaryCryptos[CoinFinded], "maxPrecision")

                print("A precisão é esta: ", maxPrecision)

                deci = Decimal(maxPrecision)
                print(deci)
                expoente = deci.as_tuple().exponent
                print("expoente: ", deci.as_tuple().exponent)
                if expoente < 0:
                    expoente = expoente * -1

                print("expoente agora: ", expoente)

                quantityToInvest = round_down(n=quantityToInvest, decimals=2)

                print("Arredondado: ", quantityToInvest)

                # Buy
                response = auth_client.place_market_order(
                    product_id='' + getattr(dictionaryCryptos[CoinFinded], "codeCoinbase") + '-EUR',
                    side='buy',
                    funds=quantityToInvest)

                print(response)

                if not "id" in response:
                    print("Error buying: ",response)
                    isStillWorthIt = False
                    continue

                if isStillWorthIt == True:
                    try:
                        while response["status"] != 'done':
                            response = auth_client.get_order(response["id"])
                    except:
                        print("Error")
                        isStillWorthIt = False
                        continue

                    print(response)

                    fileBuyLogs = open("BuyLogs", "a")
                    fileBuyLogs.write("" + str(datetime.now()) + str(response) + "\n")
                    fileBuyLogs.close()

                    print(response['filled_size'])
                    print(response['specified_funds'])

                    valueCrypto = float(response['funds']) / float(response['filled_size'])

                    print("Value Crypto: ", valueCrypto)

                    # Calculate selling Price
                    buyValue = float(response['specified_funds'])
                    proofitPretended = buyValue * profit
                    feesBuySell = (2 * buyValue) * fees
                    feeProfit = proofitPretended * fees
                    sellValue = buyValue + proofitPretended + feesBuySell + feeProfit

                    print("Valor de Venda:", sellValue)

                    sellCryptoValue = sellValue / float(response['filled_size'])

                    print("Valor Crypto na venda: ", sellCryptoValue)

                    # If buy is succed, the post a linit sell
                    if response["status"] == 'done':

                        maxPrecision = getattr(dictionaryCryptos[CoinFinded], "maxPrecision")

                        print("A precisão é esta: ", maxPrecision)

                        deci = Decimal(maxPrecision)
                        print(deci)
                        expoente = deci.as_tuple().exponent
                        print("expoente: ", deci.as_tuple().exponent)
                        if expoente < 0:
                            expoente = expoente * -1

                        print("expoente agora: ", expoente)

                        sellCryptoValue = round_up(n=sellCryptoValue, decimals=expoente)
                        print("Preço da Crypto já arredondado: ", sellCryptoValue)
                        try:
                            sellresponse = auth_client.place_limit_order(product_id=response["product_id"],
                                                                     side='sell',
                                                                     price=sellCryptoValue,
                                                                     size=float(response['filled_size']))

                            print(sellresponse)
                        except:
                            logging.basicConfig(filename="errorlogs.log",
                                                format='%(asctime)s %(message)s',
                                                filemode='a')

                            # Let us Create an object
                            logger = logging.getLogger()

                            # Now we are going to Set the threshold of logger to DEBUG
                            logger.setLevel(logging.DEBUG)

                            # some messages to test
                            logger.debug("Não deu certo")
                            logger.debug(sellresponse)

                        fileSellLogs = open("SellLogs", "a")
                        fileSellLogs.write("" + str(datetime.now()) + str(sellresponse) + "\n")
                        fileSellLogs.close()
                        return None



            if isCoinFinded:
                break
        if isStillWorthIt == False:
            isCoinFinded = False
            continue
        if isCoinFinded:
            break
        else:
            return None
















def typesCryptosInvestedAndSaveDB():
    CoinbasesecretKeySandbox = "oxMzcd0xigpV+W4cxsl2xqntrG2iYx841igfgbu646UgCMzlxcfCNqUB2nUFn79EzfynVwKj7hE8ElUipX46nA=="
    CoinbaseAPIPassSandbox = "fyhw1sn2u0h"
    CoinbaseAPIKeySandbox = "cc94e7c4d7428a8c319640509285443a"


    # Use the sandbox API (requires a different set of API access credentials)
    auth_client = cbpro.AuthenticatedClient(CoinbaseAPIKeySandbox, CoinbasesecretKeySandbox, CoinbaseAPIPassSandbox,
                                            api_url="https://api-public.sandbox.pro.coinbase.com")
    print(auth_client.get_accounts())
    profileEUR = auth_client.get_account("e4876f2e-8332-4c60-8af1-a76bdec60ce9")

    print(profileEUR["available"])

    orders = auth_client.get_orders()

    print(orders)


    counter = 0;
    for item in orders:
        print(item)
        if item["side"] == 'sell' and item["type"] == 'limit':
            counter += 1

    print(counter)



    response = auth_client.place_market_order(product_id='BTC-USD',
                                   side='buy',
                                   funds='100.00')
    print(response)

    while response["status"] != 'done':
        response = auth_client.get_order(response["id"])

    print("A compra: ",response)
    print(response['filled_size'])
    print(response['specified_funds'])

    if response["status"] == 'done':
        sellingPrice = float(response['specified_funds']) * 1.015
        print(sellingPrice)
        sellresponse = auth_client.place_limit_order(product_id='BTC-USD',
                                      side='sell',
                                      price= 101.49, #sellingPrice,
                                      size= float(response['filled_size']))


        print("A venda: ",sellresponse)

    # Create custom authentication for Exchange
    class CoinbaseExchangeAuth(AuthBase):
        def __init__(self, api_key, secret_key, passphrase):
            self.api_key = api_key
            self.secret_key = secret_key
            self.passphrase = passphrase

        def __call__(self, request):
            timestamp = str(time.time())

            message = ''.join([timestamp, request.method,
                               request.path_url, (request.body or '')])
            request.headers.update(get_auth_headers(timestamp, message,
                                                    self.api_key,
                                                    self.secret_key,
                                                    self.passphrase))
            return request

    def get_auth_headers(timestamp, message, api_key, secret_key, passphrase):
        message = message.encode('ascii')
        hmac_key = base64.b64decode(secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
        return {
            'Content-Type': 'Application/JSON',
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': api_key,
            'CB-ACCESS-PASSPHRASE': passphrase
        }

    # Buy 0.01 BTC @ 100 USD
    response = auth_client.buy(#price='100.00',  # USD
                    #size='0.01',  # BTC
                    funds='350',
                    order_type='market',
                    product_id='BTC-USD')

    print("Outra compra: ", response)

    while response["status"] != 'done':
        response = auth_client.get_order(response["id"])

    print("Depois: ", response)





    valueCrypto = float(response['funds']) / float(response['filled_size'])

    print("Value Crypto: ", valueCrypto)

    #Calculate selling Price
    buyValue = float(response['specified_funds'])
    proofitPretended = buyValue * profit
    feesBuySell = (2 * buyValue) * fees
    feeProfit = proofitPretended * fees
    sellValue = buyValue + proofitPretended + feesBuySell + feeProfit

    print("Valor de Venda:", sellValue)

    sellCryptoValue = sellValue / float(response['filled_size'])

    print("Valor Crypto na venda: ",sellCryptoValue)

    # If buy is succed, the post a linit sell
    if response["status"] == 'done':
        #sellingPrice = float(response['specified_funds']) * marginSell
        #print(sellingPrice)
        sellCryptoValue = round_up(n=sellCryptoValue, decimals=2)
        sellresponse = auth_client.place_limit_order(product_id=response["product_id"],
                                                     side='sell',
                                                     price=sellCryptoValue,
                                                     size=float(response['filled_size']))

        print(sellresponse)








    api_url = "https://api-public.sandbox.pro.coinbase.com"
    auth = CoinbaseExchangeAuth(CoinbaseAPIKeySandbox, CoinbasesecretKeySandbox, CoinbaseAPIPassSandbox)
    print(auth)
    response = requests.get(api_url + '/users/self/exchange-limits', auth=auth)



    print(response.json())








def setProfileIDCryptos(auth_client, dictionary):
    accounts = auth_client.get_accounts()
    print(accounts)

    for item in accounts:
        #print(item["currency"])
        #print(item["id"])

        for d in dictionary:

            #print(getattr(dictionary[d], "codeCoinbase"))
            if item["currency"] == getattr(dictionary[d], "codeCoinbase") and item['profile_id'] == defaultPortofolio:
                setattr(dictionary[d], "profileCoinbaseID", item["id"])
                break
    print("divisor")
    for tes in dictionary:
        print(getattr(dictionary[tes],"name"))
        print(getattr(dictionary[tes],"profileCoinbaseID"))

    return dictionary


def setMaxPrecisionCryptos(auth_client, dictionary):
    currencies = auth_client.get_currencies()
    print(currencies)

    for item in currencies:
        #print(item["currency"])
        #print(item["id"])

        for d in dictionary:

            #print(getattr(dictionary[d], "codeCoinbase"))
            if item["id"] == getattr(dictionary[d], "codeCoinbase"):
                setattr(dictionary[d], "maxPrecision", item["max_precision"])
                break
    print("divisor")
    for tes in dictionary:
        print(getattr(dictionary[tes],"name"))
        print(getattr(dictionary[tes],"maxPrecision"))

    return dictionary


def setminSizeCryptos(public_client, dictionary):
    products = public_client.get_products()
    print(products)

    print("Produtos")

    for item in products:
        #print(item["currency"])
        #print(item["id"])

        for d in dictionary:

            #print(getattr(dictionary[d], "codeCoinbase"))
            if item["id"] == (getattr(dictionary[d], "codeCoinbase") + '-EUR'):
                setattr(dictionary[d], "min", item["min_market_funds"])
                setattr(dictionary[d], "minCryptoSell", item["base_min_size"])
                setattr(dictionary[d], "maxPrecision", item["quote_increment"])
                break
    print("divisor")
    for tes in dictionary:
        print(getattr(dictionary[tes],"name"))
        print(getattr(dictionary[tes],"min"))
        print(getattr(dictionary[tes], "minCryptoSell"))
        print(getattr(dictionary[tes], "maxPrecision"))

    return dictionary


def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier


def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())

        message = ''.join([timestamp, request.method,
                           request.path_url, (request.body or '')])
        request.headers.update(get_auth_headers(timestamp, message,
                                                self.api_key,
                                                self.secret_key,
                                                self.passphrase))
        return request

def get_auth_headers(timestamp, message, api_key, secret_key, passphrase):
    message = message.encode('ascii')
    hmac_key = base64.b64decode(secret_key)
    signature = hmac.new(hmac_key, message, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
    return {
        'Content-Type': 'Application/JSON',
        'CB-ACCESS-SIGN': signature_b64,
        'CB-ACCESS-TIMESTAMP': timestamp,
        'CB-ACCESS-KEY': api_key,
        'CB-ACCESS-PASSPHRASE': passphrase
    }

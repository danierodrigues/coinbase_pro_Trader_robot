import cbpro
from vardata import numberMaxCryptosToInvest, lessHight, BCHSellMin, BTCSellMin, LTCSellMin, ETHSellMin, marginSell
import cryptoCalculations
import requests
from requests.auth import AuthBase
import time
import base64, hashlib, hmac
import numpy


def buyAndSellCoinbase(dictionaryCryptos, priorityCoinsList, auth_client, MongoClient):
    if len(dictionaryCryptos) == 0:
        return None;






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

    print("quantdade order:",quantityCryprosInvested)



    quantityToInvest = 0 #Quantity to Invest

    if quantityCryprosInvested >= numberMaxCryptosToInvest:
        return None;

    for i in range(quantityCryprosInvested + 1):
        print("iteração")
        if quantityCryprosInvested == i:
            print("entrou dentro do if")
            d = quantityCryprosInvested - i
            print("O d:",d)
            if d == 0:
                "d é igual a 0"
                d = 1
            quantityToInvest = float(moneyEUR) / d
            print("quantidade para investir:",quantityToInvest)
            break


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
                if float(cryptoAccount['balance']) != 0:
                    isCoinFinded = False
                else:
                    print("é trueeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
                    isCoinFinded = True
                    CoinFinded = d
                    percentageBelow = float(item[0])
            if isCoinFinded:
                break
        if isCoinFinded:
            break


    print("moeda encontrada ",CoinFinded)
    #Verify if the coin is still worth it
    lastValue = cryptoCalculations.knowLastValue(getattr(dictionaryCryptos[CoinFinded],"codeCoinbase") + "-EUR")
    print(lastValue)

    if lastValue['type'] == 'ticker':
        collection = db[getattr(dictionaryCryptos[CoinFinded], "name")]
        historic = collection.find()

        for his in historic:
            highter = max(his["WeekOne"][1], his["WeekTwo"][1], his["WeekThree"][1], his["WeekFour"][1])

            print(highter)
            atualPrice = float(lastValue["price"])
            x = (highter - atualPrice) / highter
            print(x)
            percentage = x * 100

            print("Is Less : ", percentage, "%")

            print(lessHight)

            if lessHight <= percentage and (percentage - 3) <= percentageBelow:
                isStillWorthIt = True
            else:
                return None

    if isStillWorthIt == True:
        #Verify if the money is suficient to buy the coin
        if CoinFinded == 'BTC':
            if (float(lastValue["price"]) * BTCSellMin) >= quantityToInvest:
                if (float(lastValue["price"]) * BTCSellMin) <= float(moneyEUR):
                    quantityToInvest = float(lastValue["price"]) * BTCSellMin
                else:
                    return None
        elif CoinFinded == 'BCH':
            if (float(lastValue["price"]) * BCHSellMin) >= quantityToInvest:
                if (float(lastValue["price"]) * BCHSellMin) <= float(moneyEUR):
                    quantityToInvest = float(lastValue["price"]) * BCHSellMin
                else:
                    return None
        elif CoinFinded == 'LTC':
            if (float(lastValue["price"]) * LTCSellMin) >= quantityToInvest:
                if (float(lastValue["price"]) * LTCSellMin) <= float(moneyEUR):
                    quantityToInvest = float(lastValue["price"]) * LTCSellMin
                else:
                    return None
        elif CoinFinded == 'ETH':
            if (float(lastValue["price"]) * ETHSellMin) >= quantityToInvest:
                if (float(lastValue["price"]) * ETHSellMin) <= float(moneyEUR):
                    quantityToInvest = float(lastValue["price"]) * ETHSellMin
                else:
                    return None
        else:
            if (float(lastValue["price"]) * getattr(dictionaryCryptos[CoinFinded], "min")) >= quantityToInvest:
                if (float(lastValue["price"]) * getattr(dictionaryCryptos[CoinFinded], "min")) <= float(moneyEUR):
                    quantityToInvest = float(lastValue["price"]) * getattr(dictionaryCryptos[CoinFinded], "min")
                else:
                    return None


    #Buy
    response = auth_client.place_market_order(product_id='' + CoinFinded + '-EUR',
                                              side='buy',
                                              funds=quantityToInvest)

    print(response)
    try:
        while response["status"] != 'done':
            response = auth_client.get_order(response["id"])
    except:
        return None

    print(response)
    print(response['filled_size'])
    print(response['specified_funds'])


    # If buy is succed, the post a linit sell
    if response["status"] == 'done':
        sellingPrice = float(response['specified_funds']) * marginSell
        print(sellingPrice)
        sellresponse = auth_client.place_limit_order(product_id=response["product_id"],
                                                     side='sell',
                                                     price= sellingPrice,
                                                     size=float(response['filled_size']))

        print(sellresponse)









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

    print(response)
    print(response['filled_size'])
    print(response['specified_funds'])

    if response["status"] == 'done':
        sellingPrice = float(response['specified_funds']) * 1.015
        print(sellingPrice)
        sellresponse = auth_client.place_limit_order(product_id='BTC-USD',
                                      side='sell',
                                      price= 101.49, #sellingPrice,
                                      size= float(response['filled_size']))


        print(sellresponse)

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
            if item["currency"] == getattr(dictionary[d], "codeCoinbase"):
                setattr(dictionary[d], "profileCoinbaseID", item["id"])
                break
    print("divisor")
    for tes in dictionary:
        print(getattr(dictionary[tes],"name"))
        print(getattr(dictionary[tes],"profileCoinbaseID"))

    return dictionary
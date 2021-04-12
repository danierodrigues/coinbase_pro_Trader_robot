
import cbpro
import requests

import excel
from pymongo import MongoClient
import cryptoCalculations
import coinbaseActions
from time import sleep
from vardata import EURAccountId, numberMaxCryptosToInvest
import logging


client = MongoClient()

public_client = cbpro.PublicClient()

AlphaVantageKey = "OGB3T91BIOCUAQ95"
CoinbasesecretKey = "rGqQm7H2BW0I+RLxI6VngMmlSTwxxf2dGaNpubRc8DH0z6won9cu3/i4/eC1TPxhj2nZRO4E1K2IxutXOvwHfA=="
CoinbaseAPIPass = "mwa296oozxm"
CoinbaseAPIKey = "e5a5d3e7edf23c0e7a61b1c4de8b257a"

CoinbasesecretKeySandbox = "oxMzcd0xigpV+W4cxsl2xqntrG2iYx841igfgbu646UgCMzlxcfCNqUB2nUFn79EzfynVwKj7hE8ElUipX46nA=="
CoinbaseAPIPassSandbox = "fyhw1sn2u0h"
CoinbaseAPIKeySandbox = "cc94e7c4d7428a8c319640509285443a"

isFirstTime = True


def entireProcessEUR(client, auth_client):



    # excel.createAndWriteExcel(currencies)

    # cryptoDictionary = excel.readAndCreateClasses(client)

    dic = excel.readClassesFromDatabase(client)
    dic = coinbaseActions.setProfileIDCryptos(auth_client=auth_client, dictionary=dic)
    #dic = coinbaseActions.setMaxPrecisionCryptos(auth_client=auth_client, dictionary=dic)
    dic = coinbaseActions.setminSizeCryptos(public_client=public_client, dictionary=dic)

    cryptoCalculations.saveHistoricCryptos(dic, public_client)

    lowestCryptosList = cryptoCalculations.calculatelowercryptos(dic, public_client, auth_client, CoinbaseAPIKey,
                                                                 CoinbasesecretKey, CoinbaseAPIPass)

    # coinbaseActions.typesCryptosInvestedAndSaveDB()

    coinbaseActions.buyAndSellCoinbase(dictionaryCryptos=dic, priorityCoinsList=lowestCryptosList,
                                       auth_client=auth_client, MongoClient=client)





if __name__ == '__main__':


    #coinbaseActions.typesCryptosInvestedAndSaveDB()

    client = MongoClient('localhost', 27017)

    #Use the Coinbase Pro API
    auth_client = cbpro.AuthenticatedClient(CoinbaseAPIKey, CoinbasesecretKey, CoinbaseAPIPass)
    # Use the sandbox API (requires a different set of API access credentials)
    #auth_client = cbpro.AuthenticatedClient(CoinbaseAPIKeySandbox, CoinbasesecretKeySandbox, CoinbaseAPIPassSandbox, api_url="https://api-public.sandbox.pro.coinbase.com")

    #print(auth_client.get_accounts())

    #currencies = auth_client.get_currencies()

    #excel.createAndWriteExcel(currencies)

    #cryptoDictionary = excel.readAndCreateClasses(client)


    while True:
        try:

            print("*********************************************************************************************************")
            print("*                                                                                                       *")
            print("*                                                                                                       *")
            print("*                                                                                                       *")
            print("*                                             Init                                                      *")
            print("*                                                                                                       *")
            print("*                                                                                                       *")
            print("*                                                                                                       *")
            print("*********************************************************************************************************")


            #API Coinbase Pro EUR Account
            profileEUR = auth_client.get_account(EURAccountId)

            #Sandbox API EUR Account
            #profileEUR = auth_client.get_account('e4876f2e-8332-4c60-8af1-a76bdec60ce9')


            print(profileEUR["available"])
            moneyEUR = profileEUR["available"]

            orders = auth_client.get_orders()

            print(orders)

            quantityCryprosInvested = 0  # Actual cryptos quantity already invested
            for item in orders:
                print(item)
                if item["side"] == 'sell' and item["type"] == 'limit':
                    quantityCryprosInvested += 1


            if float(moneyEUR) != 0 and quantityCryprosInvested <= numberMaxCryptosToInvest:
                entireProcessEUR(client, auth_client)
            else:
                print("Sleeping 30 sec.")
                sleep(30)
        except:
            print("Something went wrong")



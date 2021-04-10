from pymongo import MongoClient
import requests
import json
from datetime import datetime, timedelta
import time
from pymongo import errors
import cbpro
from websocket import create_connection
from vardata import lessHight
import heapq

#client = MongoClient()


client = MongoClient('localhost', 27017)


def saveHistoricCryptos(dictionaryCryptos, public_client):
    if len(dictionaryCryptos) == 0:
        return None;

    print("começou")

    #isLessThan24Hours = calculate24Hours(dictionaryCryptos, public_client)
    calculate30daysAgo(dictionaryCryptos, public_client)



def calculate24Hours(dictionaryCryptos, public_client):
    db = client.cryptoHistoric
    dbnames = client.database_names()
    if 'cryptoHistoric' in dbnames:
        print("It's there!")

        timeCount = time.time()
        counter = 0

        now = datetime.now()

        for items in dictionaryCryptos:

            # print(db.validate_collection(dictionaryCryptos[items]["name"]))
            # collectionsNames = db.list_collection_names()
            # print(collectionsNames)
            # print(dictionaryCryptos[items]["name"])

            # import the 'errors' module from PyMongo
            try:
                name = getattr(dictionaryCryptos[items], "name")
                col_dict = db.validate_collection(name)
                print(name + "has" + str(col_dict['nrecords']) + "documents on it.\n")
            except errors.OperationFailure as err:
                col_dict = None
                print("PyMongo ERROR:", err, "\n")

            if type(col_dict) != dict:
                print(name, "doesn't exist on server")
                continue

            while counter >= 3:
                # print(timeCount - time.time())
                if (time.time() - timeCount) >= 2:  # 1 second
                    print("entrou dentro do if")
                    print(timeCount)
                    counter = 0
                    timeCount = time.time()
            else:
                print(items)
                twentyFourHoursStats = public_client.get_product_24hr_stats(
                    '' + getattr(dictionaryCryptos[items], 'codeCoinbase') + '-EUR')
                print(twentyFourHoursStats)
                counter += 1
                if twentyFourHoursStats:
                    collection = db[items]
                    historic = collection.find()

                    for historicInformation in historic:
                        diff = now - historicInformation["UpdatedAt"]
                        diffHours = (diff.total_seconds() / 60) / 60  # hours
                        print("A diferença de horas é: " + str(diffHours))

                        isUpdated = False

                        if historicInformation['WeekOne'][0] < float(twentyFourHoursStats['low']):  # lowest
                            historicInformation['WeekOne'][0] = float(twentyFourHoursStats['low'])
                            isUpdated = True
                        if historicInformation['WeekOne'][1] > float(twentyFourHoursStats['high']):  # hight
                            historicInformation['WeekOne'][1] = float(twentyFourHoursStats['high'])
                            isUpdated = True



                    if isUpdated:
                        col = collection.update_many(
                            {"_id": historicInformation["_id"]},
                            {
                                "$set": {
                                    "WeekOne": historicInformation['WeekOne'],
                                    "WeekTwo": historicInformation['WeekTwo'],
                                    "WeekThree": historicInformation['WeekThree'],
                                    "WeekFour": historicInformation['WeekFour'],
                                    "days": historicInformation["days"],
                                    "UpdatedAt": historicInformation["UpdatedAt"]
                                },
                                # "$currentDate": {"lastModified": True}

                            }
                        )
                    # {"WeekOne": historicInformation['WeekOne'], "WeekTwo": historicInformation['WeekTwo'], "WeekThree": historicInformation['WeekThree'], "WeekFour":historicInformation['WeekFour'],"days":historicInformation["days"],"UpdatedAt":historicInformation["UpdatedAt"]})






def calculate30daysAgo(dictionaryCryptos, public_client):
    db = client.cryptoHistoric
    dbnames = client.database_names()
    if 'cryptoHistoric' in dbnames:
        client.drop_database('cryptoHistoric')

    # datetime object containing current date and time
    now = datetime.now()

    print("now =", now)

    menos = now - timedelta(days=1)
    menosIso = menos.isoformat()
    print(menosIso)

    menostrinta = menos - timedelta(days=30)
    menostrinta = menostrinta.isoformat()
    print(menostrinta)

    # historic = public_client.get_product_historic_rates('ETH-EUR',start=menostrinta , end=menosIso, granularity=86400)

    # dd/mm/YY H:M:S
    # dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    # print("date and time =", dt_string)
    timeCount = time.time()
    counter = 0
    for items in dictionaryCryptos:

        try:

            while counter >= 3:
                # print(timeCount - time.time())
                if (timeCount - time.time()) <= -1:
                    print("entrou dentro do if")
                    print(timeCount)
                    counter = 0
                    timeCount = time.time()
            else:
                print("entrou dentro do else")
                collection = db[items]
                print(items)

                response = public_client.get_product_historic_rates(
                    '' + getattr(dictionaryCryptos[items], 'codeCoinbase') + '-EUR', start=menostrinta,
                    end=menosIso, granularity=86400)
                print(type(response))
                if type(response) is list:
                    print("é igual a list")
                    weekCounter = 0
                    arrTotal = [[1000000000000000, 0], [1000000000000000, 0], [1000000000000000, 0],
                                [1000000000000000, 0], 0]  # First lowest, second hight

                    for array in response:
                        if array[1] < arrTotal[weekCounter][0]:  # lowest
                            arrTotal[weekCounter][0] = array[1]
                        if array[2] > arrTotal[weekCounter][1]:  # hight
                            arrTotal[weekCounter][1] = array[2]

                        arrTotal[4] += 1

                        if 8 < arrTotal[4] < 17:
                            weekCounter = 1
                        if 17 < arrTotal[4] < 26:
                            weekCounter = 2
                        if 26 < arrTotal[4] < 40:
                            weekCounter = 3

                    print(arrTotal)

                    data = {}
                    data["WeekOne"] = arrTotal[0]
                    data["WeekTwo"] = arrTotal[1]
                    data["WeekThree"] = arrTotal[2]
                    data["WeekFour"] = arrTotal[3]
                    data["days"] = 0
                    data["UpdatedAt"] = now

                    if data["WeekOne"][0] != 1000000000000000 and data["WeekFour"][0] != 1000000000000000 and data["WeekOne"][1] != 0 and data["WeekFour"][1] != 0:
                        post_id = collection.insert_one(data).inserted_id
                        print(post_id)

                counter += 1

        except:
            print("Error occured")

    calculate24Hours(dictionaryCryptos, public_client)






def calculatelowercryptos(dictionaryCryptos, public_client,auth_client,CoinbaseAPIKey, CoinbasesecretKey, CoinbaseAPIPass):
    if len(dictionaryCryptos) == 0:
        return None;

    lowestCryptos = [];


    client = MongoClient('localhost', 27017)
    db = client.cryptoHistoric

    dbnames = client.database_names()
    if 'cryptoHistoric' in dbnames:
        print("It's there!")


        for items in dictionaryCryptos:

            #print(db.validate_collection(dictionaryCryptos[items]["name"]))
            #collectionsNames = db.list_collection_names()
            #print(collectionsNames)
            #print(dictionaryCryptos[items]["name"])

            # import the 'errors' module from PyMongo
            try:
                name = getattr(dictionaryCryptos[items],"name")
                col_dict = db.validate_collection(name)
                print(name + "has" +  str(col_dict['nrecords']) + "documents on it.\n")
            except errors.OperationFailure as err:
                col_dict = None
                print("PyMongo ERROR:", err, "\n")

            if type(col_dict) != dict:
                print(name, "doesn't exist on server")
                continue

            print("EXISTS")



            print(getattr(dictionaryCryptos[items],"codeCoinbase") + "-EUR")
            # instantiate a WebsocketClient instance, with a Mongo collection as a parameter
            #wsClient = cbpro.WebsocketClient(url="wss://ws-feed.pro.coinbase.com", products="" + getattr(dictionaryCryptos[items],"codeCoinbase") + "-EUR",
                                             #mongo_collection=collection, should_print=False, channels=["ticker"])
            #wsClient.start()
            #time.sleep(1)
            #timeCount = time.time()
            #while (time.time() - timeCount) <= 4:
                #print("waiting");
            #lastRecord = collection.find().sort([('timestamp', -1)]).limit(2)
            #print(lastRecord[1])
            #for record in lastRecord:
                #print(record)
            #time.sleep(4)


            '''wsClient = myWebsocketClientEUR("" + getattr(dictionaryCryptos[items],"codeCoinbase"),auth_client,CoinbaseAPIKey, CoinbasesecretKey, CoinbaseAPIPass,collection)
            wsClient.start()
            print(wsClient.url, wsClient.products)
            while (wsClient.message_count < 2):
                print("\nmessage_count =", "{} \n".format(wsClient.message_count))
                time.sleep(1)'''
            #wsClient.close()

            #print("vai fechar");
            # wsClient.close()
            #print("já fechou");

            lastValue = knowLastValue(getattr(dictionaryCryptos[items],"codeCoinbase") + "-EUR")


            print(lastValue)

            if lastValue['type'] == 'ticker' and float(lastValue['price']) != 0:
                collection = db[getattr(dictionaryCryptos[items],"name")]
                historic = collection.find()

                for item in historic:
                    highter = max(item["WeekOne"][1], item["WeekTwo"][1], item["WeekThree"][1], item["WeekFour"][1])

                    print(highter)
                    atualPrice = float(lastValue["price"])
                    x = (highter - atualPrice) / highter
                    print(x)
                    percentage = x * 100

                    print("Is Less : ", percentage ,"%")

                    print(lessHight)

                    if(percentage >= lessHight):
                        array = [percentage, getattr(dictionaryCryptos[items],"name")]
                        lowestCryptos.append(array)

    print("Array lower cryptos: ",lowestCryptos)
    return lowestCryptos







def knowLastValue(product):
    URLWebSocket = "wss://ws-feed.pro.coinbase.com"

    ws = create_connection(URLWebSocket)

    params = {
        "type": "subscribe",
        "channels": [
            {"name": "ticker", "product_ids": [product]}]
    }

    counter = 0
    while True:
        ws.send(json.dumps(params))
        result = ws.recv()
        # print(result)
        #time.sleep(1)
        converted = json.loads(result)

        # print(converted)
        if converted['type'] == 'ticker' or counter >= 500:
            break;

        counter += 1
    print(counter)

    return converted




'''class myWebsocketClientEUR(cbpro.WebsocketClient):
    def __init__(self, codeCoinbase,auth_client,CoinbaseAPIKey, CoinbasesecretKey, CoinbaseAPIPass, collection):
        self.codeCoinbase = codeCoinbase
        self.auth_client = auth_client
        self.CoinbaseAPIKey = CoinbaseAPIKey
        self.CoinbasesecretKey = CoinbasesecretKey
        self.CoinbaseAPIPass = CoinbaseAPIPass
        self.collection = collection


    def on_open(self):
        self.url = "wss://ws-feed.pro.coinbase.com/"
        self.products = [self.codeCoinbase + "-EUR"]
        self.message_count = 0
        self.mongo_collection = self.collection
        self.channels = ["ticker"]
        self.auth = self.auth_client
        self.api_key = self.CoinbaseAPIKey
        self.api_secret = self.CoinbasesecretKey
        self.api_passphrase = self.CoinbaseAPIPass

        print("Lets count the messages!")

    def on_message(self, msg):
        self.message_count += 1
        if 'price' in msg and 'type' in msg:
            print("Message type:", msg["type"],
                  "\t@ {:.3f}".format(float(msg["price"])))

    def on_close(self):
        print("-- Goodbye! --")'''





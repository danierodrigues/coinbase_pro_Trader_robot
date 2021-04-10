
import xlsxwriter
import pandas as pd
import xlrd
import openpyxl
from Cryptocoin import cryptocoin as crypto


def createAndWriteExcel(currencies):
    workbook = xlsxwriter.Workbook('Criptomoedas_Coinbase.xlsx')
    worksheet = workbook.add_worksheet('Criptomoedas')

    # Start from the first cell.
    # Rows and columns are zero indexed.
    row = 0
    column = 0

    print(currencies[0]["name"])

    head=["name", "codeCoinbase", "codeAlphaVantage", "min", "proffit", "totalBuyed", "isbuyed", "isBlocked"]

    for item in head:
        worksheet.write(row,column,item)
        column += 1

    row +=1
    column = 0


    # iterating through content list
    for item in currencies:
        worksheet.write(row, column, item["name"])
        column += 1
        worksheet.write(row, column, item["id"])
        column += 1
        worksheet.write(row, column, item["id"])
        column += 1
        worksheet.write(row, column, item["min_size"])
        column += 1
        worksheet.write(row, column, 0) #proffit
        column += 1
        worksheet.write(row, column,0) #totalBuyed
        column += 1
        worksheet.write(row, column, "False")  # isbuyed
        column += 1
        worksheet.write(row, column, "False")  # isBlocked
        column = 0
        row +=1

    workbook.close()

    print("feitinho")




def readAndCreateClasses(client):



    df = pd.read_excel(r'./Criptomoedas_Coinbase.xlsx') #r'./Criptomoedas_Coinbase.xlsx')  # place "r" before the path string to address special character, such as '\'. Don't forget to put the file name at the end of the path + '.xlsx'
    #for items in df:
        #print(items)
        #continue

    #df = pd.DataFrame(df,index=[3])
    #print(df)
    #print('Excel Sheet to Dict:', df.to_dict(orient='record'))
    #print('Excel Sheet to JSON:', df.to_json(orient='records'))
    df = df.to_dict(orient='record')
    cryptoDictionary = {}

    for items in df:
        #if(isbuyed=items["isbuyed"] == "False")
        p1 = crypto(name=items["name"],codeCoinbase=items["codeCoinbase"],codeAlphaVantage=items["codeAlphaVantage"],min=items["min"],proffit=items["proffit"],totalBuyed=items["isbuyed"],isbuyed=items["isbuyed"],isBlocked=items["isBlocked"])
        #print(p1.getName())
        #isbuyed=items["isbuyed"]  isBlocked=items["isBlocked"]

        cryptoDictionary[p1.getName()] = p1



    dbnames = client.database_names()
    if 'cryptoClasses' in dbnames:
        client.drop_database('cryptoClasses')

    db = client.cryptoClasses
    collection = db.cryptoClasses
    for items in cryptoDictionary:
        data = {}
        data["name"] = getattr(cryptoDictionary[items],"name")
        data["codeCoinbase"] = getattr(cryptoDictionary[items],"codeCoinbase")
        data["codeAlphaVantage"] = getattr(cryptoDictionary[items],"codeAlphaVantage")
        data["min"] = getattr(cryptoDictionary[items],"min")
        data["proffit"] = getattr(cryptoDictionary[items],"proffit")
        data["totalBuyed"] = getattr(cryptoDictionary[items],"totalBuyed")
        data["isbuyed"] = getattr(cryptoDictionary[items],"isbuyed")
        data["isBlocked"] = getattr(cryptoDictionary[items],"isBlocked")


        cryptoClasses = db.cryptoClasses
        post_id = cryptoClasses.insert_one(data).inserted_id
        print(post_id)

    return cryptoDictionary


def readClassesFromDatabase(client):
    db = client.cryptoClasses
    collection = db.cryptoClasses

    dictionaryCrypto = {}
    classes = collection.find()
    for items in classes:

        p1 = crypto(name=items["name"], codeCoinbase=items["codeCoinbase"], codeAlphaVantage=items["codeAlphaVantage"],
                    min=items["min"], proffit=items["proffit"], totalBuyed=items["isbuyed"], isbuyed=items["isbuyed"],
                    isBlocked=items["isBlocked"])

        dictionaryCrypto[p1.getName()] = p1


    return dictionaryCrypto
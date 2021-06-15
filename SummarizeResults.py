import pandas as pd
import os
import re
import json
import csv

path = './Results'
extractedPath = './Extracted'
columnOrder = {
    "Transactions - Date":0,
    "Transactions - Description":1,
    "Transactions - Withdrawals":2,
    "Transactions - Deposits":3,
    "Transactions - Balance":4 
}

def isJSON(element:str):
    regex = re.compile('.*json')
    if regex.match(element):
        return True
    return False

def getFieldValue(fields:dict, field:str):
    return fields[field]['text']

def getFields(extraction:dict):
    return extraction["analyzeResult"]["documentResults"][0]["fields"]

def extraction(data):
    fields = getFields(data)
    extractedFields ={}
    regex = re.compile("Transactions -*")
    headers = {}
    for field in fields:
        if(regex.match(field)):
            headers[getFieldValue(fields, field)] = field
        else:
            extractedFields[field] = getFieldValue(fields, field)
    return extractedFields, headers

            
def tableExtraction(data:dict, header:dict, columnOrder:dict):
    tableColumns={}
    pages = data["analyzeResult"]['pageResults']
    rows = []
    for page in pages:
        cells = page["tables"][0]["cells"]
        oldRow = -1
        columns = ["","","","",""]
        for cell in cells:
            try:
                if(oldRow != cell['rowIndex'] and oldRow > 0):
                    rows.append(columns)
                    columns = ["","","","",""]
                if(cell['rowIndex'] == 0):
                    stdName = header[cell['text']]
                    col = cell['columnIndex']
                    tableColumns[col] = columnOrder[stdName]
                else:
                    columns[cell['columnIndex']] = cell['text']
                oldRow = cell['rowIndex']
            except:
                print("error")
        rows.append(columns)
        
    return rows
                


files = list(filter(isJSON, os.listdir(path)))
for file in files:
    content = open(os.path.join(path, file), "r")
    data = json.load(content)
    fields, headers = extraction(data)
    tableRows = tableExtraction(data ,headers, columnOrder)
    with open(os.path.join(extractedPath, file + ".csv"), "w+", newline='') as resultFile:
        writer = csv.writer(resultFile)
        for k, v in fields.items():
            if(len(k)>0):
                writer.writerow([k, v])
        for row in tableRows:
            writer.writerow(row)
        resultFile.close()





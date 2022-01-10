from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)

import grequests 
from json.decoder import JSONDecodeError
import requests
import pandas as pd
import collections
import json
import ipfshttpclient
import os
import shutil
import json
import time
from datetime import datetime
from web3 import Web3
from csv import reader
from multiprocessing import Pool
from pytz import timezone
tz = timezone('EST')


def waitForReveal(project_info):

    ipfs = project_info["ipfs"]
    contract_address = project_info["contract"]
    contract_address = Web3.toChecksumAddress(contract_address)
    ABI_ENDPOINT = 'https://api.etherscan.io/api?module=contract&action=getabi&address='
    w3 = Web3(Web3.HTTPProvider('ENTER_INFURA_URL'))
    url = ABI_ENDPOINT + contract_address
    response = requests.get(url)
    response_json = response.json()
    abi_json = json.loads(response_json['result'])
    contract = w3.eth.contract(address=contract_address, abi=abi_json)

    if ipfs == "yes":
            
        count = 1
        while True:

            if count == 5000: 
                count == 1

            token_uri = contract.functions.tokenURI(count).call()
            uri_list = token_uri.split("/")
            
            # determining if the uri includes a .
            ending = ''
            full_ending = uri_list[-1].split('.')
            if full_ending[-1] == 'json':
                ending = "." + full_ending[-1]
            project_info["ending"] = ending
                
            for value in uri_list:
                if len(value) > 30:
                    if value.startswith("Qm") | value.startswith("ba"):
                        content_identifier = value
                        project_info["ipfs_address"] = content_identifier
                        token_metadata = "https://cole.mypinata.cloud/ipfs/" + content_identifier +  "/"
                        project_info["meta_data_url"] = token_metadata
                        
            token_metadata = token_metadata + str(count) + ending
            print(token_metadata)

            try:
                response = requests.get(token_metadata)
                response = response.json()
                print(response)
                
                # catching error if key is capitilized
                try:
                    response = response["attributes"]
                except KeyError:
                    response = response["Attributes"]

            except JSONDecodeError:
                print("Tried token " + str(count) + " " + "json data not up" + " " + str(datetime.now(tz)))
                count = count + 1
                time.sleep(5)
                continue

            if response:
                print("let the show begin")
                break

            print("Tried token " + str(count) + " " + str(response) + " " + str(datetime.now(tz)))
            count = count + 1
            time.sleep(5)

    else:

        count = 1
        while True:

            if count == 5000:
                count == 1

            meta_data_url = contract.functions.tokenURI(count).call()
            print(meta_data_url)

            try:
                response = requests.get(meta_data_url,verify=False)
                print(response)
                response = response.json()
                # catching error if key is capitilized
                try:
                    response = response["attributes"]
                except KeyError:
                    response = response["Attributes"]
            
            # catches if the website is down
            except requests.exceptions.ConnectionError:
                print("Tried token " + str(count) + ", " + "website is no longer up" + " " + str(datetime.now(tz)))
                count = count + 1
                time.sleep(5)
                continue
            
            except KeyError:
                print("Tried token " + str(count) + " " + "Attributes key not up" + " " + str(datetime.now(tz)))
                count = count + 1
                time.sleep(5)
                continue
            
            except JSONDecodeError:
                print("Tried token " + str(count) + " " + "json data not up" + " " + str(datetime.now(tz)))
                count = count + 1
                time.sleep(5)
                continue

            if response:
                # keep just in case another project does something similar
                #response = response[0]
                if response["value"] == "Angry Apes United Cover":
                    print("Tried token " + str(count) + " " + "json data not up" + " " + str(datetime.now(tz)))
                    count = count + 1
                    time.sleep(5)
                    continue                    
                print("let the show begin")
                break

            print("Tried token " + str(count) + " " + str(response) + " " + str(datetime.now(tz)))
            count = count + 1
            time.sleep(5)
    
    return



def getProjectData(project_info):

    contract_address = project_info["contract"]
    contract_address = Web3.toChecksumAddress(contract_address)

    correct_supply = project_info["correct_supply"]

    ABI_ENDPOINT = 'https://api.etherscan.io/api?module=contract&action=getabi&address='
    w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/54cbe4e08c754065ab6887ddc21aa4c2'))
    
    test_token = 150
    test_token2 = 1000
    test_difference = 0

    url = ABI_ENDPOINT + contract_address
    response = requests.get(url)
    response_json = response.json()
    abi_json = json.loads(response_json['result'])
    contract = w3.eth.contract(address=contract_address, abi=abi_json)
    # result = json.dumps({"abi":abi_json}, indent=4, sort_keys=True)

    tx_hash = contract.functions.tokenURI(test_token).call()
    uri_list = tx_hash.split("/")
    uri_index = uri_list[-1]

    tx_hash2 = contract.functions.tokenURI(test_token2).call()
    uri_index2 = tx_hash2.split("/")
    uri_index2 = uri_index2[-1]
    
    # determining if the uri includes a .
    ending = ''
    full_ending = uri_list[-1].split('.')
    if full_ending[-1] == 'json':
        ending = "." + full_ending[-1]
    project_info["ending"] = ending

    try:
        uri_index = os.path.splitext(uri_index)[0]
    except TypeError:
        uri_index = uri_index

    try:
        uri_index2 = os.path.splitext(uri_index2)[0]
    except TypeError:
        uri_index2 = uri_index2

    #test_difference = test_token - int(uri_index) 
    test_difference = 0
    #test_difference2 = test_token2 - int(uri_index2) 
    test_difference2 = 0

    if test_difference != test_difference2:
        error = "user input required"
        return error
    else:
        project_info["token_fix"] = test_difference

    name = contract.functions.name().call()
    project_info["filename"] = name

    ipfs = "no"
    project_info["ipfs_address"] = ""
    for value in uri_list:
        if len(value) > 30:
            if value.startswith("Qm") | value.startswith("ba"):
                content_identifier = value
                project_info["ipfs_address"] = content_identifier
                token_metadata = "https://cole.mypinata.cloud/ipfs/" + content_identifier +  "/"
                project_info["meta_data_url"] = token_metadata
                project_info["ipfs"] = ipfs
                ipfs = "yes"

    #ipfs="no"
    project_info["ipfs"] = ipfs
    #project_info["meta_data_url"] = ""

    if ipfs == "no":
        end_count = uri_list.pop(-1)
        end_count = len(end_count)
        size_uri = len(tx_hash)
        token_metadata = tx_hash[:size_uri - 3]
        project_info["meta_data_url"] = token_metadata

    total_supply = "contract.functions." + correct_supply + "().call"
    total_supply = eval(total_supply + "()")
    project_info["total_supply"] = total_supply

    time.sleep(5)
    
    print(project_info)

    # waitForReveal(project_info)

    return(project_info)



def getProxy():

    proxy_list = []

    with open("proxy.txt",'r') as f:
        for line in f:
            a = line.split(":")
            b = a[3].rstrip('\n')
            proxies = {"http": 'http://' + a[2] + ':' + b + '@' + a[0] + ':' + a[1], 
                        "https": 'https://' + a[2] + ':' + b + '@' + a[0] + ':' + a[1]}
            proxy_list.append(proxies)

    return proxy_list



def formatProjectDic(project_info):

    # put no if not ipfs
    # if no, you do not have to worry about changing ipfs_address

    contract = project_info["contract"]
    
    project_info['open_sea_url'] = "https://opensea.io/assets/" + contract + "/"
    project_info['api_data'] = "https://api.opensea.io/api/v1/asset/" + contract + "/"

    # do not change
    filename = project_info['filename']
    file_name_csv = filename + ".csv"
    project_info['scored_file_path'] = filename + "/" + "scored" + file_name_csv
    project_info['for_sale_file_path'] = filename + "/" + "forSale" + file_name_csv

    try:
        os.mkdir(filename)
    except FileExistsError:
        shutil.rmtree(filename)
        os.mkdir(filename)

    project_info['file_path_csv'] = filename + "/" + file_name_csv

    return project_info
 


def processJson(r):

    if r != "":
        try:
            json = r.json() 
        except ValueError:
            return {"name":"unavalible"}
        except AttributeError:
            return{"name":"unavalible"}
        
        # trying to retieve the name from the metadata
        # if no name it tries for id. only have seen one 
        # project have this error
        try:
            tokenName = json["name"]
            tokenDict = {"name":tokenName}
        except KeyError:
            try:
                tokenName = json['id']
                tokenDict = {"name":tokenName}
            except KeyError:
                return{"name":"unavalible"}        

        # catching error if key is capitilized
        try:
            tokenAttribute = json["attributes"]
        except KeyError:
            tokenAttribute = json["Attributes"]
        for attribute in tokenAttribute:
            tokenValue = attribute.get("value")
            tokenTrait = attribute.get("trait_type")
            tokenDict[tokenTrait] = tokenValue
        total_attributes = len(tokenDict)
        tokenDict["Trait Count"] = total_attributes
        tokenDict = tokenDict
        return tokenDict



def getJsonInfo(urls):

    rs = (grequests.get(u) for u in urls)
    result = grequests.map(rs)   
    return result


# make it see if it excludes .json before if it sees if its numeric

def processIpfs(ipfs_address, directory_path, file_path_csv):

    api = ipfshttpclient.connect()
    api.get(ipfs_address)
    
    ipfs_path = directory_path + ipfs_address
    tokenList = []
    directory = os.fsencode(ipfs_path)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.isnumeric() != True:
            continue 
        if file.endswith == "json":
            with open(filename, 'r') as f:
                tokenDict = {}
                tokenName = f["name"]
                tokenDict = {"name":tokenName}
                tokenAttribute = f["attributes"]
                print(tokenAttribute)
                for attribute in tokenAttribute:
                    tokenValue = attribute.get("value")
                    if tokenValue == "":
                        continue
                    tokenTrait = attribute.get("trait_type")
                    tokenDict[tokenTrait] = tokenValue
                total_attributes = len(tokenDict)
                tokenDict["Trait Count"] = total_attributes
                tokenList.append(tokenDict)

        else:
            location = ipfs_path + '/' + str(filename)
            with open(location, 'r') as f:
                tokenDict = {}
                try:
                    f = json.load(f)
                except json.JSONDecodeError:
                    continue
                tokenName = f["name"]
                tokenDict = {"name":tokenName}
                tokenAttribute = f["attributes"]
                for attribute in tokenAttribute:
                    tokenValue = attribute.get("value")
                    if tokenValue == "":
                        continue
                    tokenTrait = attribute.get("trait_type")
                    tokenDict[tokenTrait] = tokenValue
                total_attributes = len(tokenDict)
                tokenDict["Trait Count"] = total_attributes
                tokenList.append(tokenDict)
    
    dataList = pd.DataFrame.from_dict(tokenList)
    dataList = dataList.fillna("None")
    dataList.to_csv(file_path_csv, mode='a', index = False)
    
    return


def makeCsv(project_info):

    pool = Pool()

    ipfs = project_info['ipfs']
    ipfs_address = project_info['ipfs_address']
    filename = project_info['filename']
    total_supply = project_info['total_supply']
    meta_data_url = project_info['meta_data_url']
    directory_path = project_info['directory_path']
    ending = project_info['ending']

    file_name_txt = filename + ".txt"
    file_name_csv = filename + ".csv"
    count = 1
    count2 = 0
    url_1 = []
    url_2 = []
    url_3 = []
    url_4 = []
    url_5 = []
    url_6 = []
    url_7 = []
    url_8 = []
    url_9 = []
    url_10 = []
    url_multiple = total_supply/10
    file_path_csv = filename + "/" + file_name_csv
    file_path_text = filename + "/" + file_name_txt

    # if ipfs == "yes":
    #     processIpfs(ipfs_address, directory_path, file_path_csv)
    #     scoreToken(project_info)  
    #     return
    
    with open(file_path_text,'w') as f:
        while count < (total_supply):
            f.write(meta_data_url + str(count) + ending + "\n")
            count += 1
    
    with open(file_path_text,'r') as f:
        for line in f:
            if count2 <= url_multiple:
                metaDataUrl2 = line.rstrip('\n')
                url_1.append(metaDataUrl2)
                count2 += 1

            elif count2 <= (url_multiple*2):
                metaDataUrl2 = line.rstrip('\n')
                url_2.append(metaDataUrl2)
                count2 += 1

            elif count2 <= (url_multiple*3):
                metaDataUrl2 = line.rstrip('\n')
                url_3.append(metaDataUrl2)
                count2 += 1

            elif count2 <= (url_multiple*4):
                metaDataUrl2 = line.rstrip('\n')
                url_4.append(metaDataUrl2)
                count2 += 1

            elif count2 <= (url_multiple*5):
                metaDataUrl2 = line.rstrip('\n')
                url_5.append(metaDataUrl2)
                count2 += 1

            elif count2 <= (url_multiple*6):
                metaDataUrl2 = line.rstrip('\n')
                url_6.append(metaDataUrl2)
                count2 += 1

            elif count2 <= (url_multiple*7):
                metaDataUrl2 = line.rstrip('\n')
                url_7.append(metaDataUrl2)
                count2 += 1

            elif count2 <= (url_multiple*8):
                metaDataUrl2 = line.rstrip('\n')
                url_8.append(metaDataUrl2)
                count2 += 1

            elif count2 <= (url_multiple*9):
                metaDataUrl2 = line.rstrip('\n')
                url_9.append(metaDataUrl2)
                count2 += 1

            elif count2 <= (total_supply):
                metaDataUrl2 = line.rstrip('\n')
                url_10.append(metaDataUrl2)
                count2 += 1
    
    url_list = [url_1, url_2, url_3, url_4, url_5, url_6, url_7, url_8, url_9, url_10] 
    all_data = []

    rs = pool.map(getJsonInfo, url_list)
    for info in rs:
        maybe = pool.map(processJson, info)
        for data in maybe:
            all_data.append(data)

    dataList = pd.DataFrame.from_dict(all_data)
    dataList = dataList.fillna("None")
    dataList.to_csv(file_path_csv, mode='a', index = False)
        
    print("tokens processed...")
    scoreToken(project_info)        


def scoreToken(project_info):

    total_supply = project_info["total_supply"]
    fileName = project_info["filename"]
    #token_fix = project_info["token_fix"]
    at_columns = 1
    token_scored = 0
    times_occured = []
    att_under_hundred = {}
    fileNameCsv = fileName + ".csv"
    filePath = fileName + "/" + fileNameCsv
    df = pd.read_csv(filePath)
    filePathScored = fileName + "/" + "scored" + fileNameCsv
    finalFile = filePathScored
    count_under_hundred = total_supply / 100

    # FIX ME
    # make a list with a dic for each column. the value for the column name
    # contains a list of dics with key value pairs for the trait and score
    # so it is able to score for the trait alone and not everything combined 

    while at_columns < len(df.columns):
        times_occured_dic = {}
        column_occured_dic = {}
        col_name = df.columns[at_columns]
        value = df.iloc[:, at_columns].values
        occurrences = collections.Counter(value)
        for k,v in occurrences.items():   
            times_occured_dic[k] = str(v)
            column_occured_dic[col_name] = times_occured_dic
        times_occured.append(column_occured_dic)
        at_columns = at_columns + 1
    print("making scoring table...") 
    
    for value in times_occured:
        for key in value:
            value = value[key]
            att_count = 0
            for k,v in value.items():
                if count_under_hundred <= int(v):
                    att_count += 1
            att_under_hundred[key] = att_count
          
    print(att_under_hundred)        
            
    while True:
        try:
            token = df.iloc[token_scored].values
            test_list = []
            list_index = 0
            at_column = 1
            # for each at column in times occured times_occured[at_column]
            # then search for the times occurered.
            for value in token:
                test_list.append(value)
            name = test_list.pop(0)
            if name == "unavalible":
                token_scored = token_scored + 1
                continue

            total = 0
            for value in test_list:
                if value == "NaN" or value == "unavalible":
                    continue
                num = times_occured[list_index]
                current_column = df.columns[at_column]
                num_under = att_under_hundred[current_column]
                num = num[current_column]
                num  = num[value]
                num = (1/(int(num)/total_supply))/(int(num_under))
                total = num + total
                at_column += 1
                list_index += 1

            tokenScore = [{"name":name,"score":total}]
            token_scored = token_scored + 1
            dataList = pd.DataFrame.from_dict(tokenScore)
            dataList.to_csv(finalFile, mode='a', index = False,header=False)
        except IndexError:
            break
    
    pre_sort = pd.read_csv(finalFile, header=None)
    pre_sort.to_csv(finalFile, header=["Name", "Score"], index=False)
    sorted_dataframe = pd.read_csv(finalFile,usecols=["Name", "Score"])
    sorted_dataframe = sorted_dataframe.sort_values(by='Score',ascending=False)
    sorted_dataframe = sorted_dataframe.reset_index(drop=True)
    sorted_dataframe.to_csv(finalFile, index=True)
    print("scored and sorted tokens...")


def getOpenSea(openSeaDic):

    salePrice = ""
    name = openSeaDic["name"]
    score = openSeaDic["score"]
    meta_data_url = openSeaDic["meta_data_url"]
    apiData = openSeaDic["apiData"]
    openSeaUrl = openSeaDic["openSeaUrl"]
    ending = openSeaDic["ending"]
    token_fix = openSeaDic["token_fix"]
    index = openSeaDic["index"]
    tokenData = {"rank":int(index)+1,"name":name, "Score":score}

    # catches error if the token is not a int. only will be fixed when 
    # i can figure out a way to get the exact token number
    try:
        tokenNumber = (''.join(filter(str.isdigit, name)))
        tokenNumber = int(tokenNumber) + int(token_fix) 
        tokenNumber = str(tokenNumber)
    except ValueError:
        print(name)
        return tokenData

    apiData = apiData + tokenNumber
    meta_data_url = meta_data_url + tokenNumber + ending
    
    headers = {"X-API-KEY": "OPENSEA_API_KEY"}
    response = requests.get(apiData, headers=headers) 
    response = response.json()

    try:
        response = response['orders']
        
    except KeyError:
        print(name)
        return tokenData
    except JSONDecodeError:
        print(name)
        return tokenData    
    for order in response:
        side = order['side']
        if side == 1:
            salePrice = order['current_price']
            salePrice = str(float(salePrice) / 1000000000000000000) + " ETH"
            break
    
    if salePrice == "":
        return tokenData
    
    # image = requests.get(meta_data_url)
    # image = image.json()
    # image = image["image"]

    #tokenData["image"] = image
    tokenData["Current Price"] = salePrice
    tokenData["Open Sea URL"] = openSeaUrl + str(tokenNumber)
    for_sale_file_path = name + '/OpenseaPrice'
    dct = {k:[v] for k,v in tokenData.items()}
    dataList = pd.DataFrame(dct)
    dataList.to_csv(for_sale_file_path, mode='a', index = False, header=False)
    return tokenData


def checkBuyPrice(project_info):

    temp_list = []
    atLine = 0
    pool = Pool()

    meta_data_url = project_info['meta_data_url']
    token_fix = project_info["token_fix"]
    open_sea_url = project_info['open_sea_url']
    api_data = project_info['api_data']
    scored_file_path= project_info['scored_file_path']
    for_sale_file_path= project_info['for_sale_file_path']
    ending = project_info['ending'] 

    with open(scored_file_path, 'r') as read_obj:
        csv_reader = reader(read_obj)

        for row in csv_reader:
            if atLine == 0:
                atLine = atLine + 1
                continue
            if atLine == 202:
                break
            
            index = row[0]
            name = row[1]
            score = row[2]
            openSeaDic = {"name":name, "score":score, "apiData":api_data,
                        "openSeaUrl":open_sea_url, "token_fix":token_fix,
                        "meta_data_url":meta_data_url, 'ending':ending,
                        'index':index}
            temp_list.append(openSeaDic)
            atLine = atLine + 1

    print("checking to see if top 200 are up for sale...")
    tokenForSale = []
    for item in temp_list:
        data = getOpenSea(item)
        tokenForSale.append(data)
        time.sleep(1)
    #tokenForSale = pool.map(getOpenSea, temp_list)
    dataList = pd.DataFrame.from_dict(tokenForSale)
    dataList.to_csv(for_sale_file_path, mode='a', index = True)


def getError(project_info):

    ipfs = project_info["ipfs"]
    filename = project_info['filename']
    file_name_csv = filename + ".csv"
    file_path_csv = filename + "/" + file_name_csv

    total_supply = project_info["total_supply"]
    total_supply_plus = int(total_supply) + 15
    total_supply_minus = int(total_supply) - 15

    total_rows = 0
    if ipfs == "yes":
        with open(file_path_csv, 'r') as read_obj:
            csv_reader = reader(read_obj)
    
            for row in csv_reader:
                total_rows += 1

            if (total_supply_minus <= total_supply) & (total_supply <=total_supply_plus):
                errors = "Total tokens graded is same as the total supply"
                return errors
            else:
                errors = "There is a discrepency in how many tokens were graded and how many there should of been"
                return errors
            

    total_fails = 0
    with open(file_path_csv, 'r') as read_obj:
        csv_reader = reader(read_obj)
        
        for row in csv_reader:
            name = row[0]
            if name == "unavalible":
                total_fails += 1

    return total_fails
    
    


        
            
            




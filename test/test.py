import dryscrape
import sys
import bs4 as bs
import urllib.request
import json
import requests
import re

rbxPlcURL = "https://rbx.place"
rolimonBaseURL = "https://www.rolimons.com/item/"
testItemID = "74174927"
testItemID2 = "439945661"

rbxPlcBuyURL = "https://rbx.place/buy/"
robux1kToUSD = 5.25
afterTax = robux1kToUSD / 1000 * 0.49


def dynamicWebScrapperInit(url):
    if 'linux' in sys.platform:
    # start xvfb in case no X is running. Make sure xvfb 
    # is installed, otherwise this won't work!
        dryscrape.start_xvfb()
    # set up a web scraping session
    sess = dryscrape.Session()
    sess.visit(url)
    source = sess.body()
    # return html body chunk
    return source

def staticWebScrapperInit(url):
    return requests.get(url).text

def rbxPlaceItemListParser(rbxPlaceItemListHtmlSource):
    soup = bs.BeautifulSoup(rbxPlaceItemListHtmlSource, 'lxml')
    test = soup.find('div', class_='shop')
    test = test.find('script')
    items = test.text[12:-1]
    # print(items)
    # f = open("shop2.txt", "r")
    # string = f.read()
    # items = string[12:-2]
    items = json.loads(items)
    return items

# Search from rolimons
def rolimonsItemSearchParser(searchedItemHtmlSource):
    # f = open("test2.txt", "r")
    soup = bs.BeautifulSoup(searchedItemHtmlSource, 'lxml')
    scripts = soup.find_all('script')
    p = re.compile('var (.*?)')
    itemDetail = None

    for script in scripts:
        if p.match(str(script.string)):
            itemDetail = json.loads((script.string).split(";")[1].split("=")[1])
    # itemDetail = json.loads(test[19].string.split(";")[1].split("=")[1])
    
    return itemDetail

def test():
    a = open("rbxplace.txt", "r")
    b = open("rolimons.txt", "r")
    rbxPlaceItemList = json.dumps(a.read())
    itemsDetail = json.loads(json.dumps(b.read()))
    profitList = []

    print(rbxPlaceItemList)
    print(itemsDetail)

    for item in rbxPlaceItemList:
        print(item)

    # for item in rbxPlaceItemList:
    #     for itemDetail in itemsDetail:
    #         if int(item["id"]) == int(itemDetail["item_id"]):
    #             profit = float(item["price"]) - (float(itemDetail["best_price"]) * afterTax)
    #             if profit > 10.0:
    #                 profit_item = {
    #                     "item_name" : item["name"],
    #                     "item_profit" : str(profit),
    #                     "item_buy_url" : rbxPlcBuyURL + item["shop"] + "/" + item["purchase_id"]
    #                 }
    #                 profitList.append(profit_item)

    # print(profitList)

def main():
    rbxPlaceItemList = rbxPlaceItemListParser(dynamicWebScrapperInit(rbxPlcURL))
    s = set()
    itemsDetail = []
    profitList = []

    for item in rbxPlaceItemList:
        if str(item["id"]) not in s and int(item["rap"]) >= 9000:
            s.add(item["id"])
            # print(item)

    for id in s:
        itemDetail = rolimonsItemSearchParser(staticWebScrapperInit(rolimonBaseURL + str(id)))
        # print(itemDetail)
        if itemDetail != None:
            itemsDetail.append(itemDetail)

    # print(itemsDetail)

    # print(rbxPlaceItemList)
    # print(itemsDetail)

    for item in rbxPlaceItemList:
        for itemDetail in itemsDetail:
            if int(item["id"]) == int(itemDetail["item_id"]):
                profit = (float(itemDetail["best_price"]) * afterTax) - float(item["price"])
                # print("name: " + item["name"])
                # print("price: " + str(item["price"]))
                # print("profit: " + str(profit))
                if profit > 10.0:
                    profit_item = {
                        "item_name" : item["name"],
                        "item_rap" : item["rap"],
                        "item_price_USD" : item["price"],
                        "item_lowest_price" : itemDetail["best_price"],
                        "item_estimated_profit" : str(profit),
                        "item_rolimon_url" : rolimonBaseURL + item["id"] ,
                        "item_buy_url" : rbxPlcBuyURL + item["shop"] + "/" + item["purchase_id"]
                    }
                    profitList.append(profit_item)

    print(profitList)

main()
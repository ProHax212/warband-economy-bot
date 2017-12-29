import cv2
import time
import numpy as np
import sys
import statistics
import threading
import queue
import msvcrt
import winsound

from pytesseract import image_to_string
from PIL import Image
from PIL import ImageGrab
from pymongo import MongoClient
from pymongo import ASCENDING
from pymongo import DESCENDING

client = MongoClient('localhost', 27017)
db = client["warband-economy"]

instructions_main = '''
--------------- INSTRUCTIONS -------------------
1 - Add new buy price
2 - Add new sell price
3 - Add new market supply modifier
4 - Add new buy/sell link
5 - Buy item
6 - Sell item
7 - Calculate sell plan
8 - Calculate buy plan
9 - Average good price
i - Print instructions
q - Quit
'''

# List of available towns on the map
available_towns = ["suno", "praven", "uxkhal", "dhirim", "reyvadin", "khudan", "curaw", "rivacheg", "tulga", "halmar", "ichamur", "narra", "sargoth", "tihr", "wercheg", "veluca", "jelkala", "yalen", "shariz", "durquba", "ahmerrad", "bariyye"]
# List of available villages on the map
available_villages = ["yaragar", "burglen", "azgad", "nomar", "emirin", "amere", "nemeja", "ryibelet", "tosdhar", "ruluns", "ehlerdah", "ibiran", "veidar", "balanli", "chide", "tadsamesh", "ushkuru", "tahlberl", "rduna", "iyindah", "tshibtin", "elberl", "yalibe", "gisim", "sumbuja", "shapeshte", "mazen", "ulburban", "hanun", "uslum", "bazeck", "shulus", "tismirr", "karindi", "vezin", "rebache", "fisdnar", "tebandra", "ayyike", "ismirala", "slezkh", "udiniad", "dusturil", "dashbigha", "tash kulun", "ada kulun", "dugan", "dirigh aban", "zagush", "peshmi", "bulugur", "amashke", "bhulaban", "kedelke", "tulbuk", "uhhun", "kulum", "haen", "mechin", "buillin", "ruvar", "ambean", "fearichen", "jayek", "jelbegi", "fenada", "aldelen", "kwynn", "rizi", "vayejeg", "odasan", "buvran", "emer", "ilvia", "ruldi", "pagundur", "glunmar", "reveran", "saren", "fedner", "epeshe", "dumar", "serindiar", "idbeles", "dirigsene", "chaeza", "sarimish", "istiniar", "chelez", "jamiche", "ayn assuadi", "dhibbain", "qalyut", "mazigh", "tamnuh", "habba", "sekhtem", "mawiti", "fishara", "iqbayl", "uzgha", "shibal", "zumr", "mijayet", "tazjunat", "aab", "hawaha", "unriya", "mit nun", "tilimsal", "rushdigh"]
available_goods = ["ale", "date fruit", "dyes", "flax bundle", "furs", "hemp", "hides", "iron", "leatherwork", "linen", "oil", "pottery", "powder", "raw silk", "salt", "shag", "spice", "tools", "velvet", "vodka", "wine", "wool", "wool cloth"]

# Print the instructions to the screen
def printInstructions():
    print()
    print(instructions_main)
    print()

# Thread to read input from keyboard
q = queue.Queue()
stopKey = 'q'
def inputThread():
    while True:
        key = msvcrt.getch().decode("utf-8")
        print("Key: %s\tStopkey: %s" % (key, stopKey))
        q.put(key)
        if key == stopKey:
            return

# Determine if a word in an integer
def isInteger(word):
    try:
        int(word)
        return True
    except:
        return False

# Use OpenCV to scan the screen for goods and their prices
def getGoodDictionaryCV():
    # Start input thread to check for quit
    t = threading.Thread(target=inputThread)
    t.start()

    lower_name_rgb = np.array([52, 55, 58], dtype="uint8")
    upper_name_rgb = np.array([232, 239, 247], dtype="uint8")

    lower_price_rgb = np.array([18, 62, 67], dtype="uint8")
    upper_price_rgb = np.array([104, 205, 217], dtype="uint8")

    goodDict = {}
    while True:
        ImageGrab.grab().save('screen_capture.png', 'PNG')

        img = cv2.imread('screen_capture.png', cv2.IMREAD_UNCHANGED)

        maskName = cv2.inRange(img, lower_name_rgb, upper_name_rgb)
        maskPrice = cv2.inRange(img, lower_price_rgb, upper_price_rgb)

        cv2.imwrite("th1.png", maskName)    # Name
        cv2.imwrite("th2.png", maskPrice)   # Price

        # Look for a good name
        print("Checking good name")
        goodName = ""
        goodImageString = image_to_string(Image.open("th1.png")).lower()
        for availableGood in available_goods:
            if availableGood in goodImageString:
                print("Found: " + availableGood)
                goodName = availableGood

        # Look for a price
        print("Checking price")
        price = 0
        for line in image_to_string(Image.open("th2.png")).split('\n'):
            if "buy price:" in line.lower() or "sell price" in line.lower():
                for word in line.split(' '):
                    if isInteger(word):
                        print("Price: " + word)
                        price = int(word)

        # Update goodDict if necessary
        print("Update dictionary")
        if goodName != "" and price != 0:
            goodDict[goodName] = price

        # Check for quit key
        try:
            key = q.get(block=False)
            print(key)
            if key == stopKey:
                break
        except queue.Empty:
            pass

        winsound.Beep(3000, 300)
        print("Sleeping")
        time.sleep(1/10)

    return goodDict

# Add a new buy price to the database
def addBuyPrice():
    # Get the place for the buy price
    place = input("Place: ")
    if place not in available_towns and place not in available_villages:
        print("Invalid place")
        return

    goodDict = getGoodDictionaryCV()
    print(goodDict)
    return

    # Keep collecting input goods for the place
    while True:
        # Get the good
        good = input("Good: ")
        if good == "q":
            break
        if good not in available_goods:
            print("Invalid Good")
            continue
        # Get the price
        price = input("Price: ")
        try:
            price = int(price)
        except:
            print("Not a number")
            continue
        
        # Get mongo collection
        collection = db["buyPrice"]

        # Check if document exists for the place/good pair
        buyPrice = collection.find_one({"place" : place, "good" : good})
        if buyPrice != None:
                # Update the price
                collection.update_one({"place" : place, "good" : good}, {"$set" : {"price" : price}})
                continue

        jsonEntry = {
                "place" : place,
                "good" : good,
                "price" : price}

        # Insert the document into the collection
        collection.insert_one(jsonEntry)

# Add a sell price for a place/good pair
def addSellPrice():
    # Get the place
    place = input("Place: ")
    if place not in available_towns and place not in available_villages:
        print("Invalid place")
        return

    # Keep getting input goods for the place
    while True:
        # Get the good
        good = input("Good: ")
        if good == "q":
            break
        if good not in available_goods:
            print("Invalid Good")
            continue

        # Get the price
        price = input("Price: ")
        try:
            price = int(price)
        except:
            print("Not an integer")
            continue
        
        # Get collections for mongo
        collection = db["sellPrice"]

        # Check if document exists
        sellPrice = collection.find_one({"place" : place, "good" : good})
        if sellPrice != None:
                # Update the price
                collection.update_one({"place" : place, "good" : good}, {"$set" : {"price" : price}})
                continue


        jsonEntry = {
                "place" : place,
                "good" : good,
                "price" : price}

        # Insert the document into the collection
        collection.insert_one(jsonEntry)

def addMarketSupplyModifier():
    place = input("Place: ")
    if place not in available_towns and place not in available_villages:
        print("Invalid place")
        return
    good = input("Good: ")
    if good not in available_goods:
        print("Invalid Good")
        return
    modifier = int(input("Modifier: "))
    if not isinstance(modifier, int):
        print("Not an integer")
        return
    
    collection = db["marketSupplyModifier"]

    # Check if document exists
    marketSupplyModifier = collection.find_one({"place" : place, "good" : good})
    if marketSupplyModifier != None:
            # Update the price
            collection.update_one({"place" : place, "good" : good}, {"$set" : {"modifier" : modifier}})
            return


    jsonEntry = {
            "place" : place,
            "good" : good,
            "modifier" : modifier}

    # Insert the document into the collection
    collection.insert_one(jsonEntry)

def addBuySellLink():
    placeOne = input("Place 1: ")
    if placeOne not in available_towns and placeOne not in available_villages:
        print("Invalid place")
        return
    placeTwo = input("Place 2: ")
    if placeTwo not in available_towns and placeTwo not in available_villages:
        print("Invalid place")
        return
    good = input("Good: ")
    if good not in available_goods:
        print("Invalid Good")
        return
    profit = int(input("Profit: "))
    if not isinstance(profit, int):
        print("Not an integer")
        return
    
    collection = db["buySellLink"]

    # Check if document exists
    buySellLink = collection.find_one({"placeOne" : placeOne, "placeTwo" : placeTwo, "good" : good})
    if buySellLink != None:
            # Update the profit
            collection.update_one({"placeOne" : placeOne, "placeTwo" : placeTwo, "good" : good}, {"$set" : {"profit" : profit}})
            return


    jsonEntry = {
            "placeOne" : placeOne,
            "placeTwo" : placeTwo,
            "good" : good,
            "profit" : profit}

    # Insert the document into the collection
    collection.insert_one(jsonEntry)

def buyItem():
    good = input("Good: ")
    if good not in available_goods:
        print("Invalid Good")
        return
    amount = int(input("Amount: "))
    if not isinstance(amount, int):
        print("Not an integer")
        return
    
    collection = db["inventory"]

    # Check if the item is already there
    buyItem = collection.find_one({"good" : good})
    if buyItem != None:
        # Update the buyItem
        collection.update_one({"good" : good}, {"$set" : {"amount" : buyItem["amount"] + amount}})
        return

    jsonEntry = {
            "good" : good,
            "amount" : amount
            }

    # Add to the database
    collection.insert_one(jsonEntry)

def sellItem():
    good = input("Good: ")
    if good not in available_goods:
        print("Invalid Good")
        return
    amount = int(input("Amount: "))
    if not isinstance(amount, int):
        print("Not an integer")
        return

    collection = db["inventory"]
    
    # Check if item is already there
    sellItem = collection.find_one({"good" : good})
    if sellItem != None:
        newAmount = max(0, sellItem["amount"] - amount)
        if newAmount == 0:
            collection.delete_one({"good" : good})
            return
        collection.update_one({"good" : good}, {"$set" : {"amount" : newAmount}}) 
        return
    else:
        print("No %s in inventory" % good)
        return

def calculateSellPlan():
    place = input("Place: ")
    if place not in available_towns and place not in available_villages:
        print("Invalid place")
        return

    buyPrice_col = db["buyPrice"]
    sellPrice_col = db["sellPrice"]

    buyPrices = {}
    for buyPrice in buyPrice_col.find({}):
        good = buyPrice["good"]
        if good not in buyPrices.keys():
            buyPrices[good] = [buyPrice["price"]]
        else:
            buyPrices[good].append(buyPrice["price"])

    # Calculate the average price for each item
    averageBuyPrices = {}
    for good, prices in buyPrices.items():
        averageBuyPrices[good] = statistics.mean(prices)

    sellPrices = {}
    for sellPrice in sellPrice_col.find({}):
        good = sellPrice["good"]
        if good not in sellPrices.keys():
            sellPrices[good] = [sellPrice["price"]]
        else:
            sellPrices[good].append(sellPrice["price"])

    # Calculate the average price for each item
    averageSellPrices = {}
    for good, prices in sellPrices.items():
        averageSellPrices[good] = statistics.mean(prices)

    # Print the goods in the place that are under the average
    for sellPrice in sellPrice_col.find({"place" : place}):
        good = sellPrice["good"]
        if sellPrice["price"] > averageSellPrices[good]:
            print("%s: %f\tBUY: %f\tSELL: %f" % (good, sellPrice["price"], averageBuyPrices[good], averageSellPrices[good]))

def calculateBuyPlan():
    place = input("Place: ")
    if place not in available_towns and place not in available_villages:
        print("Invalid place")
        return

    buyPrice_col = db["buyPrice"]
    sellPrice_col = db["sellPrice"]

    buyPrices = {}
    for buyPrice in buyPrice_col.find({}):
        good = buyPrice["good"]
        if good not in buyPrices.keys():
            buyPrices[good] = [buyPrice["price"]]
        else:
            buyPrices[good].append(buyPrice["price"])

    # Calculate the average price for each item
    averageBuyPrices = {}
    for good, prices in buyPrices.items():
        averageBuyPrices[good] = statistics.mean(prices)

    sellPrices = {}
    for sellPrice in sellPrice_col.find({}):
        good = sellPrice["good"]
        if good not in sellPrices.keys():
            sellPrices[good] = [sellPrice["price"]]
        else:
            sellPrices[good].append(sellPrice["price"])

    # Calculate the average price for each item
    averageSellPrices = {}
    for good, prices in sellPrices.items():
        averageSellPrices[good] = statistics.mean(prices)

    # Print the goods in the place that are under the average
    for buyPrice in buyPrice_col.find({"place" : place}):
        good = buyPrice["good"]
        if averageSellPrices[good] > buyPrice["price"]:
            print("%s: %f\tBUY: %f\tSELL: %f" % (good, buyPrice["price"], averageBuyPrices[good], averageSellPrices[good]))

def averageGoodPrice():
    good = input("Good: ")
    if good not in available_goods:
        print("Invalid good")
        return

    buyPrice_col = db["buyPrice"]
    sellPrice_col = db["sellPrice"]

    buyPriceList = []
    sellPriceList = []

    for buyPrice in buyPrice_col.find({"good" : good}):
        buyPriceList.append(buyPrice["price"])

    for sellPrice in sellPrice_col.find({"good" : good}):
        sellPriceList.append(sellPrice["price"])

    if len(buyPriceList) > 0:
        print("BUY PRICE") 
        print("Mean: %f" % statistics.mean(buyPriceList))
        print("Median: %f" % statistics.median(buyPriceList))
        if len(buyPriceList) > 1:
            print("Stdev: %f" % statistics.stdev(buyPriceList))
        print("")

    if len(sellPriceList) > 0:
        print("SELL PRICE")
        print("Mean: %f" % statistics.mean(sellPriceList))
        print("Median: %f" % statistics.median(sellPriceList))
        if len(sellPriceList) > 1:
            print("Stdev: %f" % statistics.stdev(sellPriceList))
        print("")

if __name__ == "__main__":
    printInstructions()
    while True:
        usr_input = input("> ")

        # Switch on input
        if usr_input == "1":
            addBuyPrice()
        elif usr_input == "2":
            addSellPrice()
        elif usr_input == "3":
            addMarketSupplyModifier()
        elif usr_input == "4":
            addBuySellLink()
        elif usr_input == "5":
            buyItem()
        elif usr_input == "6":
            sellItem()
        elif usr_input == "7":
            calculateSellPlan()
        elif usr_input == "8":
            calculateBuyPlan()
        elif usr_input == "9":
            averageGoodPrice()
        # Print instructions
        elif usr_input == "i":
            printInstructions()
        # Quit application
        elif usr_input == "q":
            sys.exit(0)
        else:
            print("Invalid command")
            printInstructions()

from pymongo import MongoClient
import sys

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
7 - Update inventory
i - Print instructions
q - Quit
'''

available_towns = ["suno", "praven", "uxkhal", "dhirim", "reyvadin", "khudan", "curaw", "rivacheg", "tulga", "halmar", "ichamur", "narra", "sargoth", "tihr", "wercheg", "veluca", "jelkala", "yalen", "shariz", "durquba", "ahmerrad", "bariyye"]
available_villages = ["yaragar", "burglen", "azgad", "nomar", "emirin", "amere", "nemeja", "ryibelet", "tosdhar", "ruluns", "ehlerdah", "ibiran", "veidar", "balanli", "chide", "tadsamesh", "ushkuru", "tahlberl", "rduna", "iyindah", "tshibtin", "elberl", "yalibe", "gisim", "sumbuja", "shapeshte", "mazen", "ulburban", "hanun", "uslum", "bazeck", "shulus", "tismirr", "karindi", "vezin", "rebache", "fisdnar", "tebandra", "ayyike", "ismirala", "slezkh", "udiniad", "dusturil", "dashbigha", "tash kulun", "ada kulun", "dugan", "dirigh aban", "zagush", "peshmi", "bulugur", "amashke", "bhulaban", "kedelke", "tulbuk", "uhhun", "kulum", "haen", "mechin", "buillin", "ruvar", "ambean", "fearichen", "jayek", "jelbegi", "fenada", "aldelen", "kwynn", "rizi", "vayejeg", "odasan", "buvran", "emer", "ilvia", "ruldi", "pagundur", "glunmar", "reveran", "saren", "fedner", "epeshe", "dumar", "serindiar", "idbeles", "dirigsene", "chaeza", "sarimish", "istiniar", "chelez", "jamiche", "ayn assuadi", "dhibbain", "qalyut", "mazigh", "tamnuh", "habba", "sekhtem", "mawiti", "fishara", "iqbayl", "uzgha", "shibal", "zumr", "mijayet", "tazjunat", "aab", "hawaha", "unriya", "mit nun", "tilimsal", "rushdigh"]
available_goods = ["ale", "date fruit", "dyes", "flax bundle", "furs", "hemp", "hides", "iron", "leatherwork", "linen", "oil", "pottery", "powder", "raw silk", "salt", "shag", "spice", "tools", "velvet", "vodka", "wine", "wool", "wool cloth"]

def printInstructions():
    print()
    print(instructions_main)
    print()

# Add a new buy price to the database
def addBuyPrice():
    place = input("Place: ")
    if place not in available_towns and place not in available_villages:
        print("Invalid place")
        return
    good = input("Good: ")
    if good not in available_goods:
        print("Invalid Good")
        return
    price = input("Price: ")
    
    collection = db["buyPrice"]

    # Check if document exists
    buyPrice = collection.find_one({"place" : place, "good" : good})
    if buyPrice != None:
            # Update the price
            buyPrice["price"] = price
            collection.update_one({"place" : place, "good" : good}, {"$set" : {"price" : price}})
            return


    jsonEntry = {
            "place" : place,
            "good" : good,
            "price" : price}

    # Insert the document into the collection
    collection.insert_one(jsonEntry)

def addSellPrice():
    place = input("Place: ")
    if place not in available_towns and place not in available_villages:
        print("Invalid place")
        return
    good = input("Good: ")
    if good not in available_goods:
        print("Invalid Good")
        return
    price = input("Price: ")
    
    collection = db["sellPrice"]

    # Check if document exists
    sellPrice = collection.find_one({"place" : place, "good" : good})
    if sellPrice != None:
            # Update the price
            collection.update_one({"place" : place, "good" : good}, {"$set" : {"price" : price}})
            return


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
    modifier = input("Modifier: ")
    
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
    profit = input("Profit: ")
    
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
        # Print instructions
        elif usr_input == "i":
            printInstructions()
        # Quit application
        elif usr_input == "q":
            sys.exit(0)
        else:
            print("Invalid command")
            printInstructions()

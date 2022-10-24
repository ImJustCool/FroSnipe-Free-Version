import requests, json, time
from bs4 import BeautifulSoup as htmlparser
from multiprocessing.pool import ThreadPool

checks = 1
ratelimits = 0
with open("config.json", "r") as jsonfile:
    config=json.load(jsonfile)
    itemIDs = config["items"]
    cookie = config["cookie"]
    webhook = config["webhook"]
    buyBellow = config["buybellow"]

payload = {"items":[]}
for x in itemIDs:
    form = {"id":x,"itemType":"Asset"}
    payload["items"].append(form)
    
with open('proxys.txt', 'r') as f:
    proxys = [line.strip() for line in f]

def updateToken():
    global s
    s = requests.session()
    s.cookies[".ROBLOSECURITY"] = cookie
    s.headers['X-CSRF-TOKEN'] = s.post("https://auth.roblox.com/v2/login").headers['X-CSRF-TOKEN']
updateToken()


while True:
    for proxy2use in proxys:
        proxies={
        "http": proxy2use,
        "https": proxy2use
                }

        def getToken():
            global csrf_token
            cookies = "GuestData=guestdatacookie;.ROBLOSECURITY=roblosecuritycookie;OtherCookies=othercookievalues"
            user_agent = "Google Chrome"

            cookie_dict = {}
            cookie_list = cookies.split(";")
            for cookie in cookie_list:
                cookie = cookie.strip()
                cookie_name, cookie_value = cookie.split("=", 1)
                cookie_dict[cookie_name] = cookie_value

            http = requests.get("https://www.roblox.com/home", cookies=cookie_dict,proxies=proxies)
            html = htmlparser(http.text, "html.parser")
            csrf_tag = html.find("meta", {"name": "csrf-token"})
            csrf_token = csrf_tag["data-token"]
        getToken()
        
        headers = {
            'Content-Type' : 'application/json',
            'X-CSRF-Token' : csrf_token,
        }
        
        
        getPrice = requests.post("https://catalog.roblox.com/v1/catalog/items/details", headers=headers, json=payload,proxies=proxies).json()
        if getPrice == {'errors': [{'code': 0, 'message': 'TooManyRequests'}]}:
            ratelimits+=1
        else:
            try:
                print(f"Checked {checks} Times. I've Been RateLimited {ratelimits} Times")
                checks +=1
                for x in getPrice["data"]:
                    lowestPrice = x["lowestPrice"]
                    itemID = x["id"]
                    productID = x["productId"]
                    if lowestPrice < buyBellow:
                        MoreDetails = s.get(f"https://economy.roblox.com/v1/assets/{itemID}/resellers").json()["data"][0]
                        DubbleCheckPrice = MoreDetails["price"]
                        if DubbleCheckPrice == lowestPrice and lowestPrice < buyBellow and DubbleCheckPrice < buyBellow:
                            itemUAID = MoreDetails["userAssetId"]
                            itemSellerID = MoreDetails["seller"]["id"]
                            Buypayload = {"expectedCurrency": 1, "expectedPrice": lowestPrice, "expectedSellerId": itemSellerID, "userAssetId": itemUAID}
                            buy = s.post(f"https://economy.roblox.com/v1/purchases/products/{productID}?1",json=Buypayload)
                            updateToken()
                            data = {"content": f"""
FroSnipe
```
😊 Just Found Somthing 😊
Cost Of Goods {lowestPrice}
Link``` https://www.roblox.com/catalog/{itemID}/
                            """}
                            print(buy.json())
                            requests.post(webhook,json=data)
            except:
                pass

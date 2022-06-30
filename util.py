import pandas as pd
import requests
import pickle
import time
import os


def remove_comma(entry):
    re = "".join(str(entry).split(","))
    return re


def add_comma(entry):
    price = remove_comma(entry)
    if str(price).isdigit():
        return f"{int(price):,}"


def configure(interval=None):
    path = os.path.join(os.path.abspath(os.curdir), "cofig")
    if os.path.exists(path) and not interval:
        with open(path, "rb") as c:
            interval = pickle.load(c)
    else:
        interval = interval if interval else 1
        with open(path, "wb") as c:
            pickle.dump(interval, c, protocol=pickle.HIGHEST_PROTOCOL)

    return interval


def get_data(url=None):
    try:
        variants = {"id": [], "seller": [], "price": [], "warranty": [], "variable": [], "lead": [], "condition": []}
        t1 = time.time()
        url = f"https://api.digikala.com/v1/product/{str(url)}/"
        js = requests.get(url).json()
        t2 = time.time()
        # print(t2-t1)
        status = js["status"]
        if status == 404:
            status = 404
        data = js["data"]["product"]
        bybox = data["default_variant"]

        if data.get("is_inactive"):
            return "inactive", None, None, None

        name = data.get("title_fa")
        category = data["category"]["code"]
        if data.get("status") in ("out_of_stock", "stop_production"):
            return data.get("status"), None, name, category

        if not data["status"] == "stop_production":
            condition = data["status"]

            if data["variants"][0].get("color"):
                variety = "color"
            elif data["variants"][0].get("size"):
                variety = "size"
            else:
                variety = None

            # add bybox variant first
            id = bybox["id"]
            selling_price = bybox["price"]["selling_price"] // 10
            seller_name = bybox["seller"]["title"]
            warranty = bybox["warranty"]["title_fa"]
            lead_time = bybox["lead_time"]
            variable = bybox[variety]["title"] if variety else " "
            variants["id"].append(id)
            variants["seller"].append(seller_name)
            variants["price"].append(selling_price)
            variants["warranty"].append(warranty)
            variants["variable"].append(variable)
            variants["lead"].append(lead_time)
            variants["condition"].append(condition)
            for variant in data["variants"]:
                id = variant["id"]
                selling_price = variant["price"]["selling_price"] // 10
                seller_name = variant["seller"]["title"]
                warranty = variant["warranty"]["title_fa"]
                lead_time = variant["lead_time"]
                variable = variant[variety]["title"] if variety else " "
                variants["id"].append(id)
                variants["seller"].append(seller_name)
                variants["price"].append(selling_price)
                variants["warranty"].append(warranty)
                variants["variable"].append(variable)
                variants["lead"].append(lead_time)
                variants["condition"].append(condition)

        if status == 404:
            return "not available"
        elif status == 200:
            return status, pd.DataFrame(variants), name, category
        else:
            print(status)
    except Exception as E:
        print(E)

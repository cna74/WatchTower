import pandas as pd
import requests
import time


def get_data(url=None):
    try:
        variants = {"id": [], "seller": [], "price": [], "warranty": [], "variable": [], "lead": [], "condition": []}
        t1 = time.time()
        url = f"https://api.digikala.com/v1/product/{url}/"
        js = requests.get(url).json()
        t2 = time.time()
        print(t2-t1)
        status = js["status"]
        if status == 404:
            status = 404
        data = js["data"]["product"]

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
                variety = "error"
            for variant in data["variants"]:
                id = variant["id"]
                selling_price = variant["price"]["selling_price"] // 10
                seller_name = variant["seller"]["title"]
                warranty = variant["warranty"]["title_fa"]
                lead_time = variant["lead_time"]
                variable = variant[variety]["title"]
                variants["id"].append(id)
                variants["seller"].append(seller_name)
                variants["price"].append(selling_price)
                variants["warranty"].append(warranty)
                variants["variable"].append(variable)
                variants["lead"].append(lead_time)
                variants["condition"].append(condition)
        # image_url = js["data"]["product"]["images"]["main"]["url"][0]
        # array = imageio.imopen(uri=image_url, io_mode="r").read()
        # image = Image.fromarray(array).resize((200, 200))
        # image.save(f"image/{url.split('/')[-2]}.png")
        #     name = "not available"
        if status == 404:
            return "not available"
        elif status == 200:
            return status, pd.DataFrame(variants), name, category
        else:
            print(status)
    except Exception as E:
        print(E)

import imageio
import requests
from PIL import Image
import exif
from collections import namedtuple

Variant = namedtuple("Variant", ["seller_name", "price", "warranty", "color", "lead_time", "coondiotion"])


def get_data(url=None):
    url = f"https://api.digikala.com/v1/product/{url}/"
    js = requests.get(url).json()
    status = js["status"]
    if status == 404:
        status = 404
    data = js["data"]["product"]
    if data.get("is_inactive"):
        status = 404
    name = data["title_fa"]
    if not data["status"] == "stop_production":
        condition = data["status"]
        variants = []
        for variant in data["variants"]:
            selling_price = variant["price"]["selling_price"] // 10
            seller_name = variant["seller"]["title"]
            warranty = variant["warranty"]["title_fa"]
            lead_time = variant["lead_time"]
            color = variant["color"]["title"]
            variants.append(Variant(seller_name, selling_price, warranty, color, lead_time, condition))
    # image_url = js["data"]["product"]["images"]["main"]["url"][0]
    # array = imageio.imopen(uri=image_url, io_mode="r").read()
    # image = Image.fromarray(array).resize((200, 200))
    # image.save(f"image/{url.split('/')[-2]}.png")
    #     name = "not available"
    if status == 404:
        return "not available"
    elif status == 200:
        return status, variants, name
    else:
        print(status)

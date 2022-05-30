import imageio
import requests
from PIL import Image
import exif


def get_data(url=None):
    url = f"https://api.digikala.com/v1/product/{url}/"
    js = requests.get(url).json()
    if js["status"] == 404:
        return "404: پیدا نشد"
    data = js["data"]["product"]
    if data.get("is_inactive"):
        return "غیرفعال"
    name = data["title_fa"]
    # for data in js["data"]["product"]["variants"]:
    #     selling_price = data["price"]["selling_price"]
    #     seller_name = data["seller"]["title"]
    #     warranty = data["warranty"]["title_fa"]
        # print(seller_name, selling_price, warranty)

    # image_url = js["data"]["product"]["images"]["main"]["url"][0]
    # array = imageio.imopen(uri=image_url, io_mode="r").read()
    # image = Image.fromarray(array).resize((200, 200))
    # image.save(f"image/{url.split('/')[-2]}.png")
    #     name = "not available"
    return name

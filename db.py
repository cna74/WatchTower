from sqlalchemy import create_engine, Column, Integer, String, select, Boolean
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import util

Base = declarative_base()


class Product(Base):
    def __init__(self, DKP, name="", category="", my_sell_price=0, bybox=0, low=0, high=0, fix_name=False):
        super(Product, self).__init__()
        # required
        self.DKP = DKP
        self.name = name
        self.my_sell_price = my_sell_price

        # optional
        self.category = category
        self.low = low
        self.high = high
        self.bybox = bybox
        self.fix_name = fix_name

    def __str__(self):
        return f"{self.DKP} - {self.name} - {self.my_sell_price}"

    __tablename__ = "product"

    def __getitem__(self, item):
        return self.name if item == "name" else None

    DKP = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String)
    category = Column(String)
    my_sell_price = Column(Integer)
    bybox = Column(Integer)
    low = Column(Integer)
    high = Column(Integer)
    fix_name = Column(Boolean)


# region create_or_connect
engine = create_engine('sqlite:///digi.db', connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
session = Session(bind=engine)
# endregion


def add(obj):
    if isinstance(obj, Product):
        if not session.scalar(select(Product).where(Product.DKP == obj.DKP)):
            session.add(obj)
            session.commit()
    else:
        raise Warning('WTF! "{}"'.format(obj.__class__))


def remove(dkp: int):
    if isinstance(dkp, int):
        product = session.query(Product).filter(Product.DKP == dkp)
        if product:
            product.delete()
            session.commit()


def edit(obj):
    try:
        if isinstance(obj, Product):
            product = session.query(Product).get(obj.DKP)
            # print(product)
            product.low = int(obj.low)
            product.high = int(obj.high)
            product.bybox = int(obj.bybox)
            product.name = str(obj.name)
            product.category = str(obj.category)

            session.commit()
    except Exception as E:
        print(f"edit {E}")


def get_products(dkp=False, category=None):
    try:
        if dkp:
            return session.scalar(select(Product.DKP))
        elif category:
            return session.query(Product).filter(Product.category == category).all()
        else:
            return session.query(Product).all()
    except Exception as E:
        print(f"get_product {E}")


def get_by_dkp(dkp):
    try:
        return session.query(Product).get(dkp)
    except Exception as E:
        print(E)


def get_categories():
    ret = [product.category for product in session.query(Product).all()]
    return set(ret)


def update_all():
    products = get_products()
    for product in products:
        status, variants, name, category = util.get_data(product.DKP)
        if product.fix_name:
            name = product.name

        if status in ("out_of_stock", "stop_production", "inactive"):
            bybox = lowest = highest = 0
            if status == "inactive":
                category = name = "Unknown"
        else:
            bybox = variants.iloc[0]["price"]
            variants = variants.sort_values(by="price")
            lowest = variants.iloc[0]["price"]
            highest = variants.iloc[-1]["price"]
        product = Product(DKP=product.DKP, name=name, category=category, my_sell_price=product.my_sell_price,
                          bybox=bybox, low=lowest, high=highest, fix_name=product.fix_name)
        edit(product)

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Product(Base):
    def __init__(self, DKP, name="", category="", my_sell_price=0, digi_sell_price=0, low=0, high=0, bybox=0):
        # required
        self.DKP = DKP
        self.name = name
        self.my_sell_price = my_sell_price

        # optional
        self.category = category
        self.low = low
        self.high = high
        self.bybox = bybox
        self.digi_sell_price = digi_sell_price

    def __str__(self):
        return f"{self.DKP} - {self.name} - {self.my_sell_price}"
    __tablename__ = "product"

    def __getitem__(self, item):
        return self.name if item == "name" else None

    DKP = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String)
    category = Column(String)
    my_sell_price = Column(Integer)
    digi_sell_price = Column(Integer)
    bybox = Column(Integer)
    low = Column(Integer)
    high = Column(Integer)


# region create_or_connect
engine = create_engine('sqlite:///digi.db', connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
session = Session(bind=engine)
# endregion


def add(obj):
    if isinstance(obj, Product):
        session.add(obj)
        session.commit()
    else:
        raise Warning('WTF! "{}"'.format(obj.__class__))


def remove(obj):
    if isinstance(obj, Product):
        product = session.query(Product).filter(Product.DKP == obj.DKP)
        if product:
            product.delete()


def get_products() -> list[Product]:
    return session.query(Product).all()

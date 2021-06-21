from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from models import *
import updater
import pandas as pd

engine = create_engine('sqlite:///data.db', echo=True)
Session = sessionmaker(bind=engine)


class ServiceError(BaseException):
    pass


# from streamlit.report_thread import get_report_ctx
#
#
# def get_session_id():
#     return get_report_ctx().session_id


# class PriceUpdater:
#     def __init__(self, symbols: list, interval: str, engine):
#         self.updaters = {
#             symbol: updater.PriceUpdater(symbol, interval, engine) for
#             symbol in symbols}
#
#     def update(self):
#         for u in self.updaters.values():
#             u.update()

def update_prices(symbols: list, intervals: list):
    for symbol in symbols:
        for interval in intervals:
            u = updater.PriceUpdater(symbol, interval, engine)
            u.update()


def is_authorised(session_id: str):
    with Session() as db:
        user = db.query(User).where(User.session_id == session_id).first()
        return True if user else False


def authenticate_user(name: str, password: str, session_id: str):
    with Session.begin() as db:
        user = db.query(User).filter_by(name=name, password=password).first()
        if not user:
            raise ValueError(f'user {name} not found')
        user.session_id = session_id
    # user = dao.get_user({'name': name, 'password': password})
    # if not user:
    #     raise ValueError(f'user {name} not found')
    # # user.session_id = session_id
    # dao.update_user(user.id, {'session_id': session_id})


def register_new_user(name: str, password: str):
    with Session.begin() as db:
        user = db.query(User).where(User.name == name).first()
        if user:
            raise ServiceError(f'user {name} already exists')
        user = User(name=name, password=password)
        db.add(user)


# def register_new_order(symbol: str, amount: int, user_id: int):
#     with Session.begin() as db:
#         order = Order(user_id=user_id, symbol=symbol, amount=amount)
#         db.add(order)


def get_user_id(session_id: str) -> int:
    with Session() as db:
        return db.query(User).where(User.session_id == session_id).one().id


# def get_orders(user_id: int) -> pd.DataFrame:
#     df = pd.read_sql(
#         f'select symbol, amount from orders where user_id == {user_id}',
#         engine, columns=['Валюта', 'Кол-во'])
#     df.index = df.index + 1
#     return df


# def get_actives(user_id: int) -> pd.DataFrame:
#     sql = 'select sum(amount) from orders where'
#     actives = pd.read_sql()

# def has_usdt_to_buy(amount: int, price: int, user_id: int) -> bool:
#     usdt_amount = get_order_by_symbol_and_user_id('USDT',
#                                                   user_id).first().amount
#     print(usdt_amount)
#     full_price = amount * price
#     # usdt_amount -= full_price
#     if full_price <= usdt_amount:
#         return True
#     return False
# def has_usdt_to_buy(amount: int, price: float, user_id: int) -> bool:
#     sql = f'select sum(amount) from orders where user_id = {user_id} and symbol = "USDT"'
#     df = pd.read_sql(sql, engine)
#     usdt_amount = df.iloc[0][0]
#     full_price = amount * price
#     if usdt_amount >= full_price:
#         return True
#     return False

def has_amount_of_symbol(symbol: str, amount: int or float, user_id: int) -> bool:
    sql = f'select sum(amount) from orders where user_id = {user_id} and symbol = "{symbol}"'
    df = pd.read_sql(sql, engine)
    symbol_amount = df.iloc[0][0]
    return amount <= symbol_amount

# def has_symbol_to_sell(symbol: str, amount: int, user_id: int) -> bool:
#     sql = f'select sum(amount) from orders where user_Id = {user_id} and symbol = "{symbol}"'
#     df = pd.read_sql(sql, engine)
#     user_symbol_amount = df.iloc[0][0]
#     return user_symbol_amount >= amount


def get_last_price(symbol: str, interval: str) -> float:
    sql = f'select close from {symbol}_{interval} order by closeTime desc limit 1'
    df = pd.read_sql(sql, engine)
    last_price = df.iloc[0][0]
    return last_price


# def get_order_by_symbol_and_user_id(symbol: str, user_id: int) -> pd.Series:
#     with Session() as db:
#         return db.query(Order).where(
#             and_(Order.symbol == symbol, Order.user_id == user_id))


def buy_symbol(symbol: str, amount: int, price: float,
               user_id: int) -> None:
    with Session.begin() as db:
        full_price = amount * price
        usdt = Order(symbol='USDT', amount=-full_price, user_id=user_id)
        symbol = Order(symbol=symbol, amount=amount, user_id=user_id)
        db.add(usdt)
        db.add(symbol)


def sell_symbol(symbol: str, amount: int, price: float,
                user_id: int) -> None:
    with Session.begin() as db:
        # price = amount * price
        usdt = Order(symbol='USDT', amount=price*amount, user_id=user_id)
        symbol = Order(symbol=symbol, amount=-amount, user_id=user_id)
        db.add(usdt)
        db.add(symbol)


def get_actives(user_id) -> pd.DataFrame:
    sql = f'select symbol, sum(amount) as amount from orders where user_id = {user_id} group by symbol'
    df = pd.read_sql(sql, engine)
    df.index = df.index + 1
    return df

    # orders = db.query(Order).where(Order.user_id == user_id).all()
    # return [f'{order.symbol}: {order.amount}' for order in orders]

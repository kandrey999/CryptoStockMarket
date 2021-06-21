import streamlit as st
from streamlit.report_thread import get_report_ctx
import service as srv
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# import dao

st.set_page_config(
    layout="wide",
    initial_sidebar_state="auto",
    page_title='docker',
    page_icon='::'
)


def get_symbols() -> list:
    return ['BTCUSDT', 'ETHUSDT', 'DOGEUSDT']


def get_intervals() -> list:
    return ['1h', '4h', '1d']


def get_session_id() -> str:
    return get_report_ctx().session_id


def validate_logged_in(session_id: str) -> None:
    if srv.is_authorised(session_id):
        st.warning(f'You already logged in')
        st.stop()


# def main_page():
#     st.text('text')


def register_new_user() -> None:
    name = st.text_input('Имя')
    password = st.text_input('Пароль')
    if st.button('Зарегистрировать'):
        srv.register_new_user(name, password)
        st.success(f'Пользователь {name} зарегистрирован')


def authorise() -> None:
    session_id = get_session_id()
    validate_logged_in(session_id)
    name = st.text_input('Имя')
    password = st.text_input('Пароль')
    if st.button('Войти'):
        srv.authenticate_user(name, password, session_id)
        st.success(f'Пользователь {name} успешно вошёл')


def validate_session() -> None:
    session_id = get_session_id()
    if not srv.is_authorised(session_id):
        st.error('Вы не авторизовались')
        st.stop()


def draw_candle(df: pd.DataFrame) -> None:
    fig = go.Figure()
    trace = go.Candlestick(x=df.openTime, open=df.open, high=df.high,
                           low=df.low, close=df.close)
    fig.add_trace(trace)
    fig.update_layout(xaxis_rangeslider_visible=False, width=1200, height=600)
    # st.write(fig)
    st.write(fig)

def show_price_graphic(symbol: int, interval: int) -> None:
    df = pd.read_sql(
        f'select * from {symbol}_{interval} order by openTime desc limit 100',
        srv.engine)
    draw_candle(df)


def buy(symbol: str, amount: int, price: float) -> None:
    # validate_amount(amount)
    # amount = int(amount)
    user_id = get_current_user_id()
    if not srv.has_amount_of_symbol('USDT', amount*price, user_id):
        st.error('Недостаточно USDT')
        st.stop()
    srv.buy_symbol(symbol, amount, price, user_id)
    st.success(f'Куплено {amount} {symbol}')


def sell(symbol: str, amount: int, price: float) -> None:
    # validate_amount(amount)
    # amount = int(amount)
    user_id = get_current_user_id()
    if not srv.has_amount_of_symbol(symbol, amount, user_id):
        st.error(f'Недостаточно {symbol}')
        st.stop()
    srv.sell_symbol(symbol, amount, price, user_id)
    st.success(f'Продано {amount} {symbol}')


def validate_amount(amount, a) -> None:
    if not (amount and amount.isnumeric()):
        # c1, cc = st.beta_columns(2)
        st.error('Введите кол-во валюты')
        # cc.error('Введите кол-во валюты')
        if a:
            st.stop()
    # amount = int(amount)
    # user_id = get_current_user_id()


def trade() -> None:
    symbols = get_symbols()
    intervals = get_intervals()
    c1, c2 = st.beta_columns(2)
    symbol = c1.selectbox('Валюта', symbols)
    interval = c1.selectbox('Интервал', intervals)
    amount = c2.text_input('Кол-во')
    # validate_amount(amount, 0)
    # symbol = st.selectbox('Валюта', symbols)
    # interval = st.selectbox('Интервал', intervals)
    show_price_graphic(symbol, interval)
    # srv.update_prices(symbols, intervals)
    # show_price_graphic(symbols, intervals)
    validate_session()
    price = srv.get_last_price(symbol, interval)
    # amount = st.text_input('Кол-во')
    # if st.button('Купить'):
    #     buy(symbol, amount, price)
    # if st.button('Продать'):
    #     sell(symbol, amount, price)
    # buy_button = st.button('Купить')
    # sell_button = st.button('Продать')
    buy_button = c2.button('Купить')
    sell_button = c2.button('Продать')
    if buy_button:
        validate_amount(amount, 1)

        buy(symbol, amount, price)
    if sell_button:
        validate_amount(amount, 1)

        sell(symbol, amount, price)

        # srv.register_new_order(symbol, amount, user_id)

    # st.success(wants_buy)


def get_current_user_id() -> int:
    session_id = get_session_id()
    return srv.get_user_id(session_id)


def actives() -> None:
    validate_session()
    user_id = get_current_user_id()
    # orders = srv.get_orders(user_id)
    actives = srv.get_actives(user_id)
    st.write('Активы')
    st.write(actives)

def show_current_user_name() -> None:
    pass


    # if amount:
    #     st.button('Купить')
    #     session_id = get_session_id()
    #     srv.register_new_order(symbol, amount, session_id)
    # st.write(f'текущая цена: {df.iloc[0, 1]}')


# def authorise_user(name, password):
#     df = pd.read_sql('users', engine)
#     names = list(df.iloc[:, 1])
#     passwords = list(df.iloc[:, 2])
#     if name in names and passwords[names.index(name)] == password:
#         st.success(f'Пользователь с именем {name} успешно вошёл')
#     else:
#         st.error('Такого пользователя нет')


# # user = pd.DataFrame([[name, password]], columns=['name', 'password'])
# df = pd.read_sql('users', engine)
# names = list(df.iloc[:, 1])
# if name not in names:
#     id_ = get_id(df.id.max())
#     user = pd.DataFrame(
#         {'id': id_, 'name': [name], 'password': [password], 'money': [100],
#          'amount': [0]})
#     user.to_sql('users', engine, index=False, if_exists='append')
#     st.success(f'Пользователь с именем {name} зарегистрирован')
# # df = pd.read_sql('users', engine)
# # df.iloc[1, 2] = 'tttt'
# # df.to_sql('users', engine, index=False, if_exists='replace')
# else:
#     st.error(f'Пользователь с именем {name} уже существует')


def main():
    pages = ['Авторизация', 'Регистрация', 'Торговля', 'Активы']
    choice = st.sidebar.radio('Навигация', pages)
    if choice == 'Авторизация':
        authorise()
    elif choice == 'Регистрация':
        register_new_user()
    elif choice == 'Торговля':
        trade()
    elif choice == 'Активы':
        actives()


if __name__ == '__main__':
    main()

# try:
#     srv.register_new_user('a', 'b')
# except srv.ServiceError as err:
#     print('')
# except BaseException:
#     print('Неожиданная ошибка')

# streamlit run app3.py --server.runOnSave true


# FROM MAIN PAGE

# df = pd.read_sql('users', engine)
# df = pd.DataFrame({'a': np.random.randn(100), 'b': np.random.randn(100)})
# df = pd.DataFrame()
# df['a'] = np.random.randn(100)
# df['b'] = np.random.randn(100)
# # st.write(df.iloc[0:2, 0:2])
# fig, ax = plt.subplots(2, 2)
# ax[0].pie([1, 2, 3])
# ax[1].hist([1, 2, 3])
# ax[2].pie([1, 2, 3])
# ax[3].hist([1, 2, 3])
# st.pyplot(fig)
# st.image('./.png')
# st.line_chart(df)
# st.date_input('time')
# st.line_chart(df)
# st.line_chart(df)
# st.bar_chart(df)
# st.pydeck_chart(df)
# v = st.select_slider('selectttt', range(100))
# st.progress(v)
# st.spinner()
# st.exception('e')
# st.balloons()
# with st.spinner('text'):
#     time.sleep(5)
#     st.success('Done')

# st.empty()
# ph = st.empty()
# st.help(pd)

import binance
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from time import sleep


class PriceUpdater:
    """
    Gets prices from server and saves to local db
    """

    def __init__(self, symbol: str, interval: str, engine):
        """
        Args:
            symbol (str)
            interval (str) 1m, 15m, 1h, 1d
        """

        self._symbol = symbol
        self._interval = interval
        self._engine = engine
        self._table = symbol + '_' + interval
        self._limit = 500

    def _get_start(self) -> pd.Timestamp:
        try:
            with self._engine.connect() as conn:
                sql = f'select openTime from {self._table} order by openTime' \
                      ' desc limit :limit'
                res = conn.execute(text(sql), {'limit': 1})
                return pd.Timestamp(res.first()[0]) + pd.Timedelta(
                    self._interval)
        except OperationalError:
            return pd.Timestamp('2021-06-01')

    def _df_from_server(self, start: pd.Timestamp) -> pd.DataFrame:
        start_ = int(start.timestamp()) * 1000
        lines = binance.klines(self._symbol, self._interval, limit=self._limit,
                               startTime=start_)
        if len(lines) == 0:
            raise ValueError()
        df = pd.DataFrame(lines)
        df['openTime'] = pd.to_datetime(df.openTime, unit='ms')
        df['closeTime'] = pd.to_datetime(df.closeTime, unit='ms')
        num_columns = ['open', 'high', 'low', 'close', 'volume', 'quoteVolume']
        df.loc[:, num_columns] = df.loc[:, num_columns].astype(float)
        return df

    def update(self) -> None:
        while True:
            try:
                start = self._get_start()
                df = self._df_from_server(start)
                print(f'update {df.openTime.iloc[0]} - {df.openTime.iloc[-1]}')
                df.to_sql(self._table, self._engine, if_exists='append',
                          index=False)
            except ValueError:
                break


class OrderUpdater:
    """
    Gets orders from server and saves to local db
    """

    def __init__(self, symbol: str, engine, limit=100):
        """
        Args:
            symbol (str)
        """

        self._symbol = symbol
        self._engine = engine
        self._limit = limit
        self._table = symbol + '_orders'

    def update(self) -> None:
        params = {"symbol": self._symbol, "limit": self._limit}
        data = binance.request("GET", "/api/v1/depth", params)
        lines = {
            "index": data["lastUpdateId"],
            "bids": {px: qty for px, qty in data["bids"]},
            "asks": {px: qty for px, qty in data["asks"]},
        }
        df = pd.DataFrame(lines)
        df['price'] = df.index
        df.to_sql(self._table, self._engine, if_exists='append', index=False)


def main():
    engine = create_engine('sqlite:///data3.db')
    updater = PriceUpdater('DOGEUSDT', '1h', engine)
    # updater = OrderUpdater('DOGEUSDT', engine)
    updater.update()

    print('Done')


if __name__ == '__main__':
    main()

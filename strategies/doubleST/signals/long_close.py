import pandas as pd


def long_sell(row: pd.DataFrame) -> dict:
    if row['close'] < row['ST_FAST_LOW'] or row['open'] < row['ST_FAST_LOW']:
        return {'signal': 'LONG_SELL', 'order': 'SELL_LIMIT', 'price': row['close']}

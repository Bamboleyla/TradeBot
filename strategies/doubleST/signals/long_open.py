import pandas as pd


def long_buy(previous: pd.DataFrame, current: pd.DataFrame) -> dict:
    if previous['close'] <= previous['ST_FAST'] and previous['close'] > previous['ST_SLOW']:
        if current['open'] > current['ST_FAST'] and current['open'] > current['ST_SLOW']:
            return {'signal': 'LONG_BUY', 'order': 'BUY_LIMIT', 'price': previous['ST_FAST']}

import pandas as pd


def long_sell(row: pd.DataFrame) -> dict:
    if row['close'] < row['ST_FAST'] or row['open'] < row['ST_FAST']:
        return {'signal': 'LONG_SELL', 'prise': row['close']}

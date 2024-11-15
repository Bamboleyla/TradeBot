import pandas as pd


def short_buy(previous: pd.DataFrame, current: pd.DataFrame) -> dict:
    if previous['ST_FAST'] > previous['ST_SLOW']:
        if previous['open'] > previous['ST_FAST'] and previous['close'] >= previous['ST_FAST']:
            if current['open'] < current['ST_FAST'] or current['close'] < current['ST_FAST']:
                return {'signal': 'SHORT_BUY', 'prise': current['close']}

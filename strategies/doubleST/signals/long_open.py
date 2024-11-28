import pandas as pd


def long_buy(previous: pd.DataFrame, current: pd.DataFrame) -> dict:
    if pd.notna(previous['ST_FAST_UP']) and pd.notna(previous['ST_SLOW_LOW']) and pd.notna(current['ST_FAST_LOW']) and pd.notna(current['ST_SLOW_LOW']):
        if previous['close'] <= previous['ST_FAST_UP'] and previous['close'] > previous['ST_SLOW_LOW']:
            if current['open'] > current['ST_FAST_LOW'] and current['open'] > current['ST_SLOW_LOW']:
                return {'signal': 'LONG_BUY', 'order': 'BUY_LIMIT', 'price': previous['ST_FAST_UP']}
